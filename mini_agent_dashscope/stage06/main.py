#!/usr/bin/env python3
"""
Stage 06: 记忆工具循环（DashScope）
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import call_chat_completion, configure_stdio, extract_assistant_text, pretty_json, read_settings, require_api_key

WORKSPACE = (Path(__file__).resolve().parent / "workspace").resolve()
MEMORY_FILE = WORKSPACE / ".agent_memory.json"
MAX_ROUNDS = 8
MAX_PREVIEW = 220


def safe_path(user_path: str) -> Path:
    """将路径约束在 workspace 下，避免越界。"""
    candidate = (WORKSPACE / user_path).resolve()
    try:
        candidate.relative_to(WORKSPACE)
    except ValueError as error:
        raise ValueError(f"路径越界: {user_path}") from error
    return candidate


def list_files(path: str = ".") -> str:
    target = safe_path(path)
    if not target.exists():
        return f"错误: 路径不存在 {path}"
    if not target.is_dir():
        return f"错误: 不是目录 {path}"
    rows: List[str] = []
    for item in sorted(target.iterdir()):
        kind = "DIR" if item.is_dir() else "FILE"
        rows.append(f"[{kind}] {item.relative_to(WORKSPACE)}")
    return "\n".join(rows) if rows else "(目录为空)"


def read_file(path: str) -> str:
    file_path = safe_path(path)
    if not file_path.exists():
        return f"错误: 文件不存在 {path}"
    if not file_path.is_file():
        return f"错误: 不是文件 {path}"
    lines = file_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return "(空文件)"
    text = "\n".join(f"{i}: {line}" for i, line in enumerate(lines, 1))
    return text if len(text) <= 8000 else text[:8000] + "\n...(已截断)"


def write_file(path: str, content: str) -> str:
    file_path = safe_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"[OK] 已写入 {file_path.relative_to(WORKSPACE)}"


def load_notes() -> List[Dict[str, Any]]:
    if not MEMORY_FILE.exists():
        return []
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_notes(notes: List[Dict[str, Any]]) -> None:
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")


def record_note(content: str, category: str = "general") -> str:
    notes = load_notes()
    notes.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "category": category,
            "content": content,
        }
    )
    save_notes(notes)
    return f"[OK] 已记录笔记 ({category})"


def recall_notes(category: str = "", limit: int = 20) -> str:
    notes = load_notes()
    if category:
        notes = [n for n in notes if n.get("category") == category]
    if not notes:
        return "暂无笔记"
    sliced = notes[-max(1, min(limit, 100)) :]
    lines: List[str] = []
    for idx, note in enumerate(sliced, 1):
        ts = note.get("timestamp", "")
        cat = note.get("category", "general")
        content = note.get("content", "")
        lines.append(f"{idx}. [{cat}] {content} ({ts})")
    return "\n".join(lines)


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出目录内容",
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
            "description": "读取文件并附带行号",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_note",
            "description": "记录一条会话笔记",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "category": {"type": "string"},
                },
                "required": ["content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_notes",
            "description": "回忆历史笔记",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "limit": {"type": "integer"},
                },
            },
        },
    },
]


def parse_args(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        return json.loads(raw)
    return {}


def run_tool(name: str, arguments: Dict[str, Any]) -> str:
    try:
        if name == "list_files":
            return list_files(path=str(arguments.get("path", ".")))
        if name == "read_file":
            return read_file(path=str(arguments["path"]))
        if name == "write_file":
            return write_file(path=str(arguments["path"]), content=str(arguments["content"]))
        if name == "record_note":
            return record_note(content=str(arguments["content"]), category=str(arguments.get("category", "general")))
        if name == "recall_notes":
            return recall_notes(category=str(arguments.get("category", "")), limit=int(arguments.get("limit", 20)))
        return f"错误: 未知工具 {name}"
    except Exception as error:  # noqa: BLE001
        return f"错误: 工具执行失败 - {error}"


def agent_loop(task: str, max_rounds: int) -> int:
    settings = read_settings()
    require_api_key(settings)
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "你是本地工作助手。请优先使用工具再回答。"
                "你有记忆工具 record_note/recall_notes，可跨轮次保存关键信息。"
            ),
        },
        {"role": "user", "content": task},
    ]

    print("workspace:", WORKSPACE)
    print("memory:", MEMORY_FILE)
    print("task:", task)

    for i in range(1, max_rounds + 1):
        print(f"\n=== Round {i}/{max_rounds} ===")
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

        messages.append(
            {
                "role": "assistant",
                "content": content if isinstance(content, str) else "",
                "tool_calls": tool_calls if tool_calls else None,
            }
        )

        if not tool_calls:
            print("\n--- Final Assistant ---")
            print(extract_assistant_text(response_json) or "(空)")
            return 0

        for call in tool_calls:
            fn = call.get("function", {})
            tool_name = fn.get("name", "")
            raw = fn.get("arguments", "{}")
            try:
                args = parse_args(raw)
            except json.JSONDecodeError:
                args = {}
            print(f"\nTool Call: {tool_name}")
            print("Args:", pretty_json(args))
            result = run_tool(tool_name, args)
            preview = result[:MAX_PREVIEW] + ("..." if len(result) > MAX_PREVIEW else "")
            print("Result Preview:", preview)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", ""),
                    "name": tool_name,
                    "content": result,
                }
            )

    print("达到最大轮次，任务可能未完成。")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="记忆工具循环")
    parser.add_argument(
        "--task",
        default="请记录我的偏好：回答简洁、先给结论后给步骤；然后回忆这些偏好并输出两条执行建议。",
    )
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    args = parser.parse_args()

    configure_stdio()
    try:
        return agent_loop(task=args.task, max_rounds=args.max_rounds)
    except RuntimeError as error:
        print(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
