#!/usr/bin/env python3
"""
Stage 02: 文本编辑工具
在 read/write 基础上增加 edit 功能
"""

import os
from pathlib import Path

def read_tool(file_path: str) -> str:
    """读取文件内容并返回带行号的字符串"""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"错误: 文件 '{file_path}' 不存在"
        # 逐行读取文件并构建带行号的列表，方便 LLM 参照
        lines = path.read_text(encoding='utf-8').splitlines()
        numbered = [f"{idx}: {line}" for idx, line in enumerate(lines, 1)]
        return "\n".join(numbered) if numbered else "(空文件)"
    except Exception as error:
        return f"错误: 读取文件失败 - {error}"

def write_tool(file_path: str, content: str) -> str:
    """将内容写入指定文件"""
    try:
        path = Path(file_path)
        # 确保父目录存在后写入内容，避免因路径不存在导致失败
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return f"✓ 写入文件: {file_path}"
    except Exception as error:
        return f"错误: 写入文件失败 - {error}"

def edit_tool(file_path: str, old_text: str, new_text: str) -> str:
    """在文件中查找 old_text 并替换为 new_text"""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"错误: 文件 '{file_path}' 不存在"
        content = path.read_text(encoding='utf-8')
        # 只在找到目标文本后才写回，避免误写
        if old_text not in content:
            return "错误: 未找到需要替换的文本"
        path.write_text(content.replace(old_text, new_text), encoding='utf-8')
        return f"✓ 成功替换文本: {old_text} -> {new_text}"
    except Exception as error:
        return f"错误: 编辑文件失败 - {error}"

def main() -> int:
    """测试 read/write/edit 工具"""
    print("=== nanocode_dashscope Stage 02: 文本编辑工具 ===\n")
    sample_file = "stage02_sample.txt"
    initial_content = "TODO: replace me\n第二行保持不变"
    
    # 写入初始内容
    print("--- 写入初始内容 ---")
    print(write_tool(sample_file, initial_content))
    
    # 读取初始内容
    print("\n--- 初始内容 ---")
    print(read_tool(sample_file))
    
    # 执行编辑操作
    print("\n--- 执行 edit 工具 ---")
    print(edit_tool(sample_file, "TODO: replace me", "DONE"))
    
    # 读取编辑后内容
    print("\n--- 编辑后内容 ---")
    print(read_tool(sample_file))
    
    # 清理测试文件
    try:
        os.remove(sample_file)
        print(f"\n✓ 清理测试文件: {sample_file}")
    except OSError:
        pass
    
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
