#!/usr/bin/env python3
"""
Stage 04: 手写工具调用循环（DashScope OpenAI 兼容）
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import (
    call_chat_completion,
    configure_stdio,
    extract_assistant_text,
    pretty_json,
    read_settings,
    require_api_key,
)

WORKSPACE = (Path(__file__).resolve().parent / "workspace").resolve()
MAX_ROUNDS = 8
MAX_PREVIEW = 200


def safe_path(user_path: str) -> Path:
    """将用户路径约束在本 stage 的 workspace 下。"""
    candidate = (WORKSPACE / user_path).resolve()
    try:
        candidate.relative_to(WORKSPACE)
    except ValueError as error:
        raise ValueError(f"路径越界: {user_path}") from error
    return candidate


def tool_list_files(path: str = ".") -> str:
    base = safe_path(path)
    if not base.exists():
        return f"错误: 路径不存在: {path}"
    if not base.is_dir():
        return f"错误: 不是目录: {path}"

    items: List[str] = []
    for item in sorted(base.iterdir()):
        kind = "DIR" if item.is_dir() else "FILE"
        rel = item.relative_to(WORKSPACE)
        items.append(f"[{kind}] {rel}")
    if not items:
        return "(目录为空)"
    return "\n".join(items[:100])


def tool_read_file(path: str) -> str:
    file_path = safe_path(path)
    if not file_path.exists():
        return f"错误: 文件不存在: {path}"
    if not file_path.is_file():
        return f"错误: 不是文件: {path}"
    content = file_path.read_text(encoding="utf-8")
    if not content:
        return "(空文件)"
    lines = content.splitlines()
    numbered = [f"{idx}: {line}" for idx, line in enumerate(lines, 1)]
    text = "\n".join(numbered)
    if len(text) > 8000:
        return text[:8000] + "\n...(已截断)"
    return text


def tool_write_file(path: str, content: str) -> str:
    file_path = safe_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    rel = file_path.relative_to(WORKSPACE)
    return f"[OK] 已写入 {rel}"


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出目录中的文件与子目录",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "相对 workspace 的目录路径"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件内容并附带行号",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "相对 workspace 的文件路径"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件（不存在则创建）",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "相对 workspace 的文件路径"},
                    "content": {"type": "string", "description": "完整文件内容"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


def dispatch_tool(name: str, arguments: Dict[str, Any]) -> str:
    """按工具名分发执行。"""
    try:
        if name == "list_files":
            return tool_list_files(path=str(arguments.get("path", ".")))
        if name == "read_file":
            return tool_read_file(path=str(arguments["path"]))
        if name == "write_file":
            return tool_write_file(path=str(arguments["path"]), content=str(arguments["content"]))
        return f"错误: 未知工具 {name}"
    except Exception as error:  # noqa: BLE001
        return f"错误: 工具执行失败 - {error}"


def parse_tool_args(raw_arguments: Any) -> Dict[str, Any]:
    if isinstance(raw_arguments, dict):
        return raw_arguments
    if isinstance(raw_arguments, str):
        if not raw_arguments.strip():
            return {}
        return json.loads(raw_arguments)
    return {}


def run_loop(task: str, max_rounds: int) -> int:
    settings = read_settings()
    require_api_key(settings)

    WORKSPACE.mkdir(parents=True, exist_ok=True)

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "你是一个本地编码助手。"
                "你可以调用 list_files/read_file/write_file 工具。"
                "必须优先使用工具获取文件信息，不要臆造文件内容。"
            ),
        },
        {"role": "user", "content": task},
    ]

    print("workspace:", WORKSPACE)
    print("task:", task)

    for round_idx in range(1, max_rounds + 1):
        print(f"\n=== Round {round_idx}/{max_rounds} ===")
        response_json = call_chat_completion(
            settings=settings,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            timeout=60,
        )

        message = response_json.get("choices", [{}])[0].get("message", {})
        content = message.get("content")
        tool_calls = message.get("tool_calls") or []

        # 关键：把 assistant 原消息回填，保持上下文完整。
        messages.append(
            {
                "role": "assistant",
                "content": content if isinstance(content, str) else "",
                "tool_calls": tool_calls if tool_calls else None,
            }
        )

        if not tool_calls:
            final_text = extract_assistant_text(response_json)
            print("\n--- Final Assistant ---")
            print(final_text or "(空)")
            return 0

        for tool_call in tool_calls:
            fn = tool_call.get("function", {})
            name = fn.get("name", "")
            raw_args = fn.get("arguments", "{}")

            try:
                args = parse_tool_args(raw_args)
            except json.JSONDecodeError:
                args = {}

            print(f"\nTool Call: {name}")
            print("Args:", pretty_json(args))
            tool_result = dispatch_tool(name=name, arguments=args)
            preview = tool_result[:MAX_PREVIEW] + ("..." if len(tool_result) > MAX_PREVIEW else "")
            print("Result Preview:", preview)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", ""),
                    "name": name,
                    "content": tool_result,
                }
            )

    print("达到最大轮次，任务可能未完成。")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="手写 DashScope function calling 循环")
    parser.add_argument(
        "--task",
        default="请在 notes/todo.md 中写入 3 条学习任务，然后读取该文件并给我一个简短总结。",
    )
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    args = parser.parse_args()

    configure_stdio()

    try:
        return run_loop(task=args.task, max_rounds=args.max_rounds)
    except RuntimeError as error:
        print(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
