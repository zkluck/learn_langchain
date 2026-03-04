#!/usr/bin/env python3
"""
Stage 03: 通过 mini-agent CLI 执行单任务
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import configure_stdio


def main() -> int:
    parser = argparse.ArgumentParser(description="通过 mini-agent CLI 执行单任务")
    parser.add_argument(
        "--task",
        default="请在当前目录创建 hello_dashscope.txt，内容为：Hello DashScope + Mini-Agent!",
        help="传给 mini-agent 的任务文本",
    )
    parser.add_argument("--timeout", type=int, default=300, help="子进程超时秒数")
    args = parser.parse_args()

    configure_stdio()

    mini_agent_cmd = shutil.which("mini-agent")
    if not mini_agent_cmd:
        print("未找到 mini-agent 命令。请先安装：")
        print("uv tool install git+https://github.com/MiniMax-AI/Mini-Agent.git")
        return 1

    workspace = Path(__file__).resolve().parent / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    command = [
        mini_agent_cmd,
        "--workspace",
        str(workspace),
        "--task",
        args.task,
    ]

    print("=== mini_agent_dashscope Stage 03: mini-agent 单任务 ===")
    print("执行命令：")
    print(" ".join(command))
    print()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"执行超时（{args.timeout}s）")
        return 1

    print("--- STDOUT ---")
    print(result.stdout.strip() or "(空)")
    if result.stderr.strip():
        print("\n--- STDERR ---")
        print(result.stderr.strip())

    hello_file = workspace / "hello_dashscope.txt"
    if hello_file.exists():
        print("\n检测到产物文件：")
        print(hello_file)
        print(hello_file.read_text(encoding="utf-8"))

    print(f"\n退出码: {result.returncode}")
    return 0 if result.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
