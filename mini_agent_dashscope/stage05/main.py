#!/usr/bin/env python3
"""
Stage 05: 端到端验收脚本
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import configure_stdio


def run_step(name: str, script: Path, args: list[str] | None = None, timeout: int = 300) -> bool:
    command = [sys.executable, str(script)]
    if args:
        command.extend(args)

    print(f"\n=== {name} ===")
    print("Command:", " ".join(command))
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print("FAILED: timeout")
        return False

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print("--- STDERR ---")
        print(result.stderr.strip())

    ok = result.returncode == 0
    print("STATUS:", "PASS" if ok else "FAIL")
    return ok


def main() -> int:
    configure_stdio()
    root = Path(__file__).resolve().parents[1]

    checks = [
        ("Stage00 环境检查", root / "stage00" / "main.py", []),
        ("Stage01 配置生成", root / "stage01" / "main.py", ["--overwrite"]),
        ("Stage02 API 连通", root / "stage02" / "main.py", []),
        (
            "Stage04 工具循环",
            root / "stage04" / "main.py",
            [
                "--task",
                "请写入 reports/check.md 内容为 `DashScope E2E OK`，然后读取该文件并回复完成。",
                "--max-rounds",
                "6",
            ],
        ),
    ]

    all_ok = True
    for name, script, script_args in checks:
        ok = run_step(name=name, script=script, args=script_args)
        all_ok = all_ok and ok
        if not ok:
            break

    if all_ok:
        print("\nALL CHECKS PASSED")
        return 0

    print("\nCHECK FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
