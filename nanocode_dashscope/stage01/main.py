#!/usr/bin/env python3
"""
Stage 01: 文件读写工具
实现基础的文件读取和写入功能
"""

import os
from pathlib import Path

def read_tool(file_path: str) -> str:
    """
    读取文件内容并添加行号
    
    Args:
        file_path: 文件路径
        
    Returns:
        带行号的文件内容
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"错误: 文件 '{file_path}' 不存在"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 添加行号
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i}: {line.rstrip()}")
        
        return '\n'.join(numbered_lines)
    
    except PermissionError:
        return f"错误: 没有权限读取文件 '{file_path}'"
    except Exception as e:
        return f"错误: 读取文件时发生异常 - {e}"

def write_tool(file_path: str, content: str) -> str:
    """
    将内容写入文件
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        
    Returns:
        操作结果信息
    """
    try:
        path = Path(file_path)
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✓ 成功写入文件: {file_path} (内容长度: {len(content)} 字符)"
    
    except PermissionError:
        return f"错误: 没有权限写入文件 '{file_path}'"
    except Exception as e:
        return f"错误: 写入文件时发生异常 - {e}"

def main():
    """主函数：测试文件读写工具"""
    print("=== nanocode_dashscope Stage 01: 文件读写工具 ===\n")
    
    # 测试写入工具
    print("--- 测试 write 工具 ---")
    test_file = "test.txt"
    test_content = "Hello, World!\n这是测试文件内容。\n包含多行文本。"
    
    result = write_tool(test_file, test_content)
    print(result)
    
    # 测试读取工具
    print("\n--- 测试 read 工具 ---")
    print(f"文件内容: {test_file}")
    content = read_tool(test_file)
    print(content)
    
    # 清理测试文件
    try:
        os.remove(test_file)
        print(f"\n✓ 清理测试文件: {test_file}")
    except:
        pass
    
    # 显示工具定义
    print("\n--- 工具定义 ---")
    print("read: 读取文件内容并显示行号")
    print("write: 将内容写入文件")
    
    return 0

if __name__ == "__main__":
    exit(main())
