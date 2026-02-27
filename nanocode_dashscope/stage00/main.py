#!/usr/bin/env python3
"""
Stage 00: 环境检查
验证 Python 版本和环境变量配置
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """检查 Python 版本是否为 3.11+"""
    # 读取当前解释器的版本号，确认是否满足最低要求
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (需要 3.11+)")
        return False

def check_env_var(name, default=None):
    """检查环境变量"""
    # 拉取环境变量值，如果允许则回退到默认值
    value = os.getenv(name, default)
    if value:
        print(f"✓ {name}: {value}")
        return True
    else:
        print(f"✗ {name} 未设置")
        return False

def main():
    """主函数：执行所有环境检查"""
    print("=== nanocode_dashscope Stage 00: 环境检查 ===\n")
    
    # 检查 Python 版本，确保后续示例可运行
    python_ok = check_python_version()
    
    print("\n--- 环境变量检查 ---")
    
    # 检查必需的环境变量，缺失时直接阻塞
    api_key_ok = check_env_var("OPENAI_API_KEY")
    
    # 检查可选的环境变量（提供默认值方便快速体验）
    base_url_ok = check_env_var(
        "OPENAI_BASE_URL", 
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    )
    model_ok = check_env_var("MODEL", "openai:qwen3-max")
    
    print("\n--- 检查结果 ---")
    
    if python_ok and api_key_ok and base_url_ok and model_ok:
        print("环境检查通过，可以进入下一阶段")
        return 0
    else:
        print("环境检查失败，请修复上述问题后重试")
        return 1

if __name__ == "__main__":
    sys.exit(main())
