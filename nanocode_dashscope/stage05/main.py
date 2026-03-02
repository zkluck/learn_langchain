#!/usr/bin/env python3
"""
Stage 05: 构造请求 Payload
演示如何使用 Python 组装 DashScope 兼容的请求体
"""

import json
import os
from typing import Dict, Any, List

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "读取文件内容并显示行号",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件路径"
                    }
                },
                "required": ["file_path"]
            }
        }
    }
]


def build_messages() -> List[Dict[str, str]]:
    """构造演示所需的消息列表"""
    # 这里的消息用于模拟一次最简单的读取需求
    return [
        {
            "role": "user",
            "content": "请读取 README.md 的第一行"
        }
    ]


def build_payload() -> Dict[str, Any]:
    """组装完整 payload，包含模型、消息、工具等字段"""
    # 模型支持通过环境变量覆盖，便于实验不同 DashScope 模型
    payload: Dict[str, Any] = {
        "model": os.getenv("MODEL", "qwen3-max"),
        "messages": build_messages(),
        "tools": TOOLS,
        "tool_choice": "auto",
    }
    return payload


def main() -> int:
    """打印格式化后的请求体，验证结构是否正确"""
    print("=== nanocode_dashscope Stage 05: 构造请求 Payload ===\n")
    # 构建 payload 并以 JSON 美化输出，方便拷贝到后续阶段
    payload = build_payload()
    print("--- 请求体 ---")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
