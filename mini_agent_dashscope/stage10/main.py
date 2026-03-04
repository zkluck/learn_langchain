#!/usr/bin/env python3
"""
Stage 10: 进阶总验收
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import configure_stdio


def run_step(name: str, script: Path, args: List[str] | None = None, timeout: int = 300) -> Tuple[bool, str]:
    command = [sys.executable, str(script)]
    if args:
        command.extend(args)
    print(f"\n=== {name} ===")
    print("command:", " ".join(command))
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("status: FAIL (timeout)")
        return False, "timeout"

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print("--- STDERR ---")
        print(result.stderr.strip())

    ok = result.returncode == 0
    print("status:", "PASS" if ok else "FAIL")
    return ok, f"exit={result.returncode}"


def main() -> int:
    parser = argparse.ArgumentParser(description="mini_agent_dashscope 总验收")
    parser.add_argument("--strict-mini-agent", action="store_true", help="要求 stage09 也必须通过")
    args = parser.parse_args()

    configure_stdio()
    root = Path(__file__).resolve().parents[1]

    required_steps = [
        ("Stage02 API 连通", root / "stage02" / "main.py", []),
        (
            "Stage06 记忆循环",
            root / "stage06" / "main.py",
            ["--max-rounds", "6"],
        ),
        (
            "Stage07 全工具循环",
            root / "stage07" / "main.py",
            ["--max-rounds", "6"],
        ),
        ("Stage08 MCP 配置", root / "stage08" / "main.py", ["--overwrite"]),
    ]

    all_required_ok = True
    for name, script, step_args in required_steps:
        ok, _ = run_step(name=name, script=script, args=step_args, timeout=240)
        all_required_ok = all_required_ok and ok
        if not ok:
            break

    if not all_required_ok:
        print("\nREQUIRED CHECK FAILED")
        return 1

    mini_agent_exists = bool(shutil.which("mini-agent"))
    if not mini_agent_exists:
        print("\nmini-agent 命令不存在，跳过 Stage09（可选）。")
        if args.strict_mini_agent:
            print("strict 模式下视为失败。")
            return 1
        print("ALL REQUIRED CHECKS PASSED")
        return 0

    ok09, _ = run_step(
        name="Stage09 日志回放",
        script=root / "stage09" / "main.py",
        args=["--show-log-tail", "12"],
        timeout=300,
    )
    if args.strict_mini_agent:
        if ok09:
            print("\nALL CHECKS PASSED")
            return 0
        print("\nSTRICT CHECK FAILED")
        return 1

    if ok09:
        print("\nALL CHECKS PASSED")
    else:
        print("\nALL REQUIRED CHECKS PASSED（Stage09 可选失败）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
