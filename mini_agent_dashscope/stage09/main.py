#!/usr/bin/env python3
"""
Stage 09: 调用 mini-agent 并回放日志统计
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import configure_stdio


def find_latest_log(log_dir: Path, before: set[Path]) -> Path | None:
    candidates = {p for p in log_dir.glob("agent_run_*.log")} - before
    if candidates:
        return max(candidates, key=lambda p: p.stat().st_mtime)
    existed = list(log_dir.glob("agent_run_*.log"))
    if not existed:
        return None
    return max(existed, key=lambda p: p.stat().st_mtime)


def parse_log_stats(log_text: str) -> Dict[str, int]:
    return {
        "request_count": len(re.findall(r"\]\s+REQUEST", log_text)),
        "response_count": len(re.findall(r"\]\s+RESPONSE", log_text)),
        "tool_result_count": len(re.findall(r"\]\s+TOOL_RESULT", log_text)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="运行 mini-agent 并分析日志")
    parser.add_argument(
        "--task",
        default="请在当前目录创建 report.md，写入三条 DashScope + Mini-Agent 使用建议。",
    )
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--show-log-tail", type=int, default=30, help="显示日志末尾行数")
    args = parser.parse_args()

    configure_stdio()

    mini_agent_cmd = shutil.which("mini-agent")
    if not mini_agent_cmd:
        print("未找到 mini-agent 命令。请先安装：")
        print("uv tool install git+https://github.com/MiniMax-AI/Mini-Agent.git")
        return 1

    workspace = Path(__file__).resolve().parent / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    log_dir = Path.home() / ".mini-agent" / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    before_logs = set(log_dir.glob("agent_run_*.log"))

    command = [mini_agent_cmd, "--workspace", str(workspace), "--task", args.task]
    print("=== mini_agent_dashscope Stage 09: 运行并回放日志 ===")
    print("command:", " ".join(command))

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"执行超时（{args.timeout}s）")
        return 1

    if proc.stdout.strip():
        print("\n--- STDOUT ---")
        print(proc.stdout.strip())
    if proc.stderr.strip():
        print("\n--- STDERR ---")
        print(proc.stderr.strip())
    print(f"\nexit_code: {proc.returncode}")

    log_file = find_latest_log(log_dir=log_dir, before=before_logs)
    if not log_file:
        print("未找到日志文件。")
        return 1

    text = log_file.read_text(encoding="utf-8", errors="replace")
    stats = parse_log_stats(text)
    print("\n--- Log Summary ---")
    print("log_file:", log_file)
    print("request_count:", stats["request_count"])
    print("response_count:", stats["response_count"])
    print("tool_result_count:", stats["tool_result_count"])

    if args.show_log_tail > 0:
        tail = "\n".join(text.splitlines()[-args.show_log_tail :])
        print("\n--- Log Tail ---")
        print(tail)

    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
