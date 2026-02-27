#!/usr/bin/env python3
"""
Stage 03: Shell 与搜索工具
实现 glob/grep/bash 三个基础工具
"""

import os
from pathlib import Path
import glob
import re
import shlex
import subprocess
from typing import List


def glob_tool(pattern: str) -> List[str]:
    """使用 glob 模式搜索文件"""
    # 借助 glob 递归匹配文件，方便模型了解可用文件
    matches = glob.glob(pattern, recursive=True)
    return matches


def grep_tool(pattern: str, file_pattern: str = "*") -> List[str]:
    """在符合 file_pattern 的文件中用正则查找 pattern"""
    matches: List[str] = []
    # 遍历匹配到的文件，逐行执行正则搜索
    for file_path in glob.glob(file_pattern, recursive=True):
        path = Path(file_path)
        if not path.is_file():
            continue
        try:
            for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append(f"{file_path}:{idx}: {line}")
        except OSError:
            continue
    return matches


def bash_tool(command: str) -> str:
    """执行 shell 命令并返回输出、错误、退出码"""
    if not command.strip():
        return "错误: 命令不能为空"
    try:
        # 使用 shell=False 执行命令，避免命令注入风险
        command_args = shlex.split(command, posix=(os.name != "nt"))
        result = subprocess.run(
            command_args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except ValueError as error:
        return f"错误: 命令解析失败 - {error}"
    except OSError as error:
        return f"错误: 命令执行失败 - {error}"
    except subprocess.TimeoutExpired:
        return "错误: 命令执行超时 (15 秒)"
    output = []
    if result.stdout.strip():
        output.append(f"输出:\n{result.stdout.strip()}")
    if result.stderr.strip():
        output.append(f"错误:\n{result.stderr.strip()}")
    output.append(f"退出码: {result.returncode}")
    return "\n".join(output)


def main() -> int:
    """演示 glob/grep/bash 工具"""
    print("=== nanocode_dashscope Stage 03: Shell 与搜索工具 ===\n")

    print("--- glob 示例 ---")
    # 展示如何列出当前目录下的 Markdown 文件
    files = glob_tool("*.md")
    if files:
        print("找到以下 Markdown 文件:")
        for name in files[:5]:
            print(f"- {name}")
        if len(files) > 5:
            print(f"... 共 {len(files)} 个文件")
    else:
        print("未找到任何 Markdown 文件")

    print("\n--- grep 示例 ---")
    # 搜索包含关键词 nanocode 的文件内容
    matches = grep_tool(r"nanocode", "*.md")
    if matches:
        print("找到以下匹配:")
        for line in matches[:5]:
            print(line)
        if len(matches) > 5:
            print(f"... 共 {len(matches)} 处匹配")
    else:
        print("未找到包含 'nanocode' 的内容")

    print("\n--- bash 示例 ---")
    # 执行目录列举命令展示目录结构（兼容 Windows/Linux/macOS）
    list_command = "cmd /c dir" if os.name == "nt" else "ls"
    print(bash_tool(list_command))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
