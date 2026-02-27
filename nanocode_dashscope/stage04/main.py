#!/usr/bin/env python3
"""
Stage 04: 工具 Schema 生成
将工具定义转换为 DashScope/OpenAI 兼容的 function calling schema
"""

import json
from typing import Dict, List, Any

# 定义所有工具的元数据，后续直接复用
TOOLS: Dict[str, Dict[str, Any]] = {
    "read": {
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
    },
    "write": {
        "description": "将内容写入文件",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要写入的文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "要写入的文本"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    "edit": {
        "description": "在文件中查找并替换文本",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要编辑的文件路径"
                },
                "old_text": {
                    "type": "string",
                    "description": "需要被替换的旧文本"
                },
                "new_text": {
                    "type": "string",
                    "description": "新的文本内容"
                }
            },
            "required": ["file_path", "old_text", "new_text"]
        }
    },
    "glob": {
        "description": "使用 glob 模式搜索文件",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "glob 搜索模式，如 *.py"
                }
            },
            "required": ["pattern"]
        }
    },
    "grep": {
        "description": "在文件中搜索文本模式",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "要搜索的正则表达式"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "匹配文件的 glob 模式",
                    "default": "*"
                }
            },
            "required": ["pattern"]
        }
    },
    "bash": {
        "description": "执行 shell 命令",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的 shell 命令"
                }
            },
            "required": ["command"]
        }
    }
}

def make_schema() -> List[Dict[str, Any]]:
    """将工具元数据转换为 function calling schema 列表"""
    schema: List[Dict[str, Any]] = []
    # 遍历工具字典，为每个工具生成符合 OpenAI function calling 的描述
    for name, meta in TOOLS.items():
        schema.append({
            "type": "function",
            "function": {
                "name": name,
                "description": meta["description"],
                "parameters": meta["parameters"]
            }
        })
    return schema

def main() -> int:
    """打印 schema 及格式化 JSON"""
    print("=== nanocode_dashscope Stage 04: 工具 Schema 生成 ===\n")
    # 调用生成函数获取完整 schema 列表
    schema = make_schema()
    print(f"工具数量: {len(schema)}\n")
    # 以美观的 JSON 格式输出，方便复制至后续阶段
    print(json.dumps(schema, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
