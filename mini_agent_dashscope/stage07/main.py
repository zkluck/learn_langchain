#!/usr/bin/env python3
"""
Stage 07: 全工具循环（含可选 Bash）
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import call_chat_completion, configure_stdio, extract_assistant_text, pretty_json, read_settings, require_api_key

WORKSPACE = (Path(__file__).resolve().parent / "workspace").resolve()
MAX_ROUNDS = 8
MAX_PREVIEW = 260


def safe_path(user_path: str) -> Path:
    candidate = (WORKSPACE / user_path).resolve()
    try:
        candidate.relative_to(WORKSPACE)
    except ValueError as error:
        raise ValueError(f"路径越界: {user_path}") from error
    return candidate


def in_workspace(path: Path) -> bool:
    try:
        path.resolve().relative_to(WORKSPACE)
        return True
    except ValueError:
        return False


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def list_files(path: str = ".") -> str:
    base = safe_path(path)
    if not base.exists():
        return f"错误: 路径不存在 {path}"
    if not base.is_dir():
        return f"错误: 不是目录 {path}"
    items: List[str] = []
    for item in sorted(base.iterdir()):
        items.append(f"[{'DIR' if item.is_dir() else 'FILE'}] {rel(item)}")
    return "\n".join(items) if items else "(目录为空)"


def read_file(path: str) -> str:
    file_path = safe_path(path)
    if not file_path.exists():
        return f"错误: 文件不存在 {path}"
    if not file_path.is_file():
        return f"错误: 不是文件 {path}"
    lines = file_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return "(空文件)"
    return "\n".join(f"{i}: {line}" for i, line in enumerate(lines, 1))


def write_file(path: str, content: str) -> str:
    file_path = safe_path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"[OK] 已写入 {rel(file_path)}"


def edit_file(path: str, old_text: str, new_text: str) -> str:
    file_path = safe_path(path)
    if not file_path.exists():
        return f"错误: 文件不存在 {path}"
    text = file_path.read_text(encoding="utf-8")
    if old_text not in text:
        return "错误: 未找到待替换文本"
    file_path.write_text(text.replace(old_text, new_text), encoding="utf-8")
    return f"[OK] 已编辑 {rel(file_path)}"


def glob_files(pattern: str) -> str:
    matched: List[str] = []
    for raw in glob.glob(pattern, recursive=True):
        path = Path(raw)
        if not in_workspace(path):
            continue
        matched.append(rel(path))
    if not matched:
        return f"未匹配到: {pattern}"
    preview = "\n".join(matched[:50])
    return f"共 {len(matched)} 个:\n{preview}"


def grep_text(pattern: str, file_pattern: str = "**/*") -> str:
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        return f"错误: 正则非法 - {error}"

    rows: List[str] = []
    for raw in glob.glob(file_pattern, recursive=True):
        path = Path(raw)
        if not path.is_file() or not in_workspace(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines, 1):
            if compiled.search(line):
                rows.append(f"{rel(path)}:{idx}: {line}")
        if len(rows) >= 100:
            break
    if not rows:
        return f"未找到匹配: {pattern}"
    return "\n".join(rows[:100])


def bash_run(command: str, timeout: int = 20) -> str:
    if os.getenv("ENABLE_BASH_TOOL", "0") != "1":
        return "错误: bash 工具默认关闭，请设置 ENABLE_BASH_TOOL=1"
    if not command.strip():
        return "错误: 命令不能为空"
    try:
        args = shlex.split(command, posix=(os.name != "nt"))
    except ValueError as error:
        return f"错误: 命令解析失败 - {error}"
    try:
        result = subprocess.run(
            args,
            shell=False,
            cwd=str(WORKSPACE),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return "错误: 命令不存在"
    except subprocess.TimeoutExpired:
        return f"错误: 命令超时 ({timeout}s)"
    except OSError as error:
        return f"错误: 命令执行失败 - {error}"

    parts: List[str] = []
    if result.stdout.strip():
        parts.append(f"stdout:\n{result.stdout.strip()}")
    if result.stderr.strip():
        parts.append(f"stderr:\n{result.stderr.strip()}")
    parts.append(f"exit_code: {result.returncode}")
    return "\n".join(parts)


TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "列出目录",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文件",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "编辑文件（替换文本）",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob_files",
            "description": "glob 搜索文件",
            "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_text",
            "description": "正则搜索文本",
            "parameters": {
                "type": "object",
                "properties": {"pattern": {"type": "string"}, "file_pattern": {"type": "string"}},
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash_run",
            "description": "执行命令（默认关闭，需 ENABLE_BASH_TOOL=1）",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}, "timeout": {"type": "integer"}},
                "required": ["command"],
            },
        },
    },
]


def parse_tool_args(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str) and raw.strip():
        return json.loads(raw)
    return {}


def dispatch(name: str, arguments: Dict[str, Any]) -> str:
    try:
        if name == "list_files":
            return list_files(path=str(arguments.get("path", ".")))
        if name == "read_file":
            return read_file(path=str(arguments["path"]))
        if name == "write_file":
            return write_file(path=str(arguments["path"]), content=str(arguments["content"]))
        if name == "edit_file":
            return edit_file(
                path=str(arguments["path"]),
                old_text=str(arguments["old_text"]),
                new_text=str(arguments["new_text"]),
            )
        if name == "glob_files":
            return glob_files(pattern=str(arguments["pattern"]))
        if name == "grep_text":
            return grep_text(
                pattern=str(arguments["pattern"]),
                file_pattern=str(arguments.get("file_pattern", "**/*")),
            )
        if name == "bash_run":
            return bash_run(
                command=str(arguments["command"]),
                timeout=int(arguments.get("timeout", 20)),
            )
        return f"错误: 未知工具 {name}"
    except Exception as error:  # noqa: BLE001
        return f"错误: 工具执行失败 - {error}"


def loop(task: str, max_rounds: int) -> int:
    settings = read_settings()
    require_api_key(settings)
    WORKSPACE.mkdir(parents=True, exist_ok=True)

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "你是本地工程助手。"
                "遇到文件问题必须先调用工具获取事实，不要猜测。"
                "当任务完成时，给出简短结果与产物路径。"
            ),
        },
        {"role": "user", "content": task},
    ]

    print("workspace:", WORKSPACE)
    print("task:", task)
    print("ENABLE_BASH_TOOL:", os.getenv("ENABLE_BASH_TOOL", "0"))

    for idx in range(1, max_rounds + 1):
        print(f"\n=== Round {idx}/{max_rounds} ===")
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
            name = fn.get("name", "")
            raw_args = fn.get("arguments", "{}")
            try:
                args = parse_tool_args(raw_args)
            except json.JSONDecodeError:
                args = {}
            print(f"\nTool Call: {name}")
            print("Args:", pretty_json(args))
            result = dispatch(name=name, arguments=args)
            preview = result[:MAX_PREVIEW] + ("..." if len(result) > MAX_PREVIEW else "")
            print("Result Preview:", preview)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", ""),
                    "name": name,
                    "content": result,
                }
            )

    print("达到最大轮次，任务可能未完成。")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="全工具循环")
    parser.add_argument(
        "--task",
        default=(
            "请创建 docs/guide.md，写入三行学习清单；"
            "再把“学习清单”替换为“执行清单”；"
            "然后搜索包含“执行清单”的文件并总结结果。"
        ),
    )
    parser.add_argument("--max-rounds", type=int, default=MAX_ROUNDS)
    args = parser.parse_args()

    configure_stdio()
    try:
        return loop(task=args.task, max_rounds=args.max_rounds)
    except RuntimeError as error:
        print(error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
