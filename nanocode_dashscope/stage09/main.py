#!/usr/bin/env python3
"""
Stage 09: 完整示例汇总
集成所有功能的完整 agentic loop 实现
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
import subprocess
import glob
import re
from typing import Dict, List, Any, Optional

# 工具实现
def read_tool(file_path: str) -> str:
    """读取文件内容并添加行号"""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"错误: 文件 '{file_path}' 不存在"
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        numbered_lines = []
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i}: {line.rstrip()}")
        
        return '\n'.join(numbered_lines)
    except Exception as e:
        return f"错误: 读取文件失败 - {e}"

def write_tool(file_path: str, content: str) -> str:
    """将内容写入文件"""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"✓ 成功写入文件: {file_path}"
    except Exception as e:
        return f"错误: 写入文件失败 - {e}"

def edit_tool(file_path: str, old_text: str, new_text: str) -> str:
    """编辑文件内容"""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"错误: 文件 '{file_path}' 不存在"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if old_text not in content:
            return f"错误: 在文件中未找到要替换的文本"
        
        new_content = content.replace(old_text, new_text)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"✓ 成功编辑文件: {file_path}"
    except Exception as e:
        return f"错误: 编辑文件失败 - {e}"

def glob_tool(pattern: str) -> str:
    """使用 glob 模式搜索文件"""
    try:
        files = glob.glob(pattern, recursive=True)
        if not files:
            return f"未找到匹配 '{pattern}' 的文件"
        
        return f"找到 {len(files)} 个文件:\n" + '\n'.join(files)
    except Exception as e:
        return f"错误: 搜索文件失败 - {e}"

def grep_tool(pattern: str, file_pattern: str = "*") -> str:
    """在文件中搜索文本模式"""
    try:
        files = glob.glob(file_pattern, recursive=True)
        matches = []
        
        for file_path in files:
            if Path(file_path).is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            matches.append(f"{file_path}:{i}: {line.rstrip()}")
                except:
                    # 跳过无法读取的文件
                    continue
        
        if not matches:
            return f"未找到匹配模式 '{pattern}' 的内容"
        
        return f"找到 {len(matches)} 个匹配:\n" + '\n'.join(matches[:20])  # 限制输出
    except Exception as e:
        return f"错误: 搜索内容失败 - {e}"

def bash_tool(command: str) -> str:
    """执行 shell 命令"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        output = []
        if result.stdout:
            output.append(f"输出:\n{result.stdout}")
        if result.stderr:
            output.append(f"错误:\n{result.stderr}")
        
        output.append(f"退出码: {result.returncode}")
        
        return '\n'.join(output)
    except subprocess.TimeoutExpired:
        return "错误: 命令执行超时 (30秒)"
    except Exception as e:
        return f"错误: 执行命令失败 - {e}"

# 工具定义和 schema
TOOLS = {
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
                    "description": "要写入的内容"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    "edit": {
        "description": "编辑文件内容，替换指定文本",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要编辑的文件路径"
                },
                "old_text": {
                    "type": "string",
                    "description": "要被替换的文本"
                },
                "new_text": {
                    "type": "string",
                    "description": "替换后的新文本"
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
                    "description": "要搜索的正则表达式模式"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "文件搜索模式，默认为 *",
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
    """生成工具的 JSON schema"""
    tools = []
    for name, tool in TOOLS.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
        })
    return tools

# API 调用
def call_api(messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """调用 DashScope API"""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
    model = os.getenv("MODEL", "openai:qwen3-max")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY 环境变量未设置")
    
    # 构造请求数据
    data = {
        "model": model,
        "messages": messages
    }
    
    if tools:
        data["tools"] = tools
        data["tool_choice"] = "auto"
    
    # 发送请求
    req = urllib.request.Request(
        base_url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        try:
            error_detail = json.loads(e.read().decode('utf-8'))
            error_msg += f" - {error_detail.get('error', {}).get('message', '')}"
        except:
            pass
        raise Exception(error_msg)
    except Exception as e:
        raise Exception(f"API 调用失败: {e}")

# 工具执行
def execute_tool_call(tool_call: Dict[str, Any]) -> str:
    """执行工具调用"""
    function_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    
    tool_functions = {
        "read": lambda: read_tool(**arguments),
        "write": lambda: write_tool(**arguments),
        "edit": lambda: edit_tool(**arguments),
        "glob": lambda: glob_tool(**arguments),
        "grep": lambda: grep_tool(**arguments),
        "bash": lambda: bash_tool(**arguments)
    }
    
    if function_name not in tool_functions:
        return f"错误: 未知工具 '{function_name}'"
    
    try:
        return tool_functions[function_name]()
    except Exception as e:
        return f"工具执行失败: {e}"

# 主循环
def main():
    """主函数：交互式代理循环"""
    print("=== nanocode_dashscope Stage 09: 完整代理 ===\n")
    
    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: OPENAI_API_KEY 环境变量未设置")
        return 1
    
    messages = []
    tools_schema = make_schema()
    
    print("🤖 输入你的问题 (输入 /c 清空历史, /q 退出):")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if user_input == "/q":
                print("\n👋 再见！")
                break
            elif user_input == "/c":
                messages = []
                print("\n🧹 对话历史已清空")
                continue
            elif not user_input:
                continue
            
            # 添加用户消息
            messages.append({"role": "user", "content": user_input})
            
            # 调用 API
            try:
                response = call_api(messages, tools_schema)
                message = response["choices"][0]["message"]
                
                # 处理工具调用
                if message.get("tool_calls"):
                    # 添加助手消息（包含工具调用）
                    messages.append(message)
                    
                    # 执行每个工具调用
                    for tool_call in message["tool_calls"]:
                        print(f"\n🔧 调用工具: {tool_call['function']['name']}({tool_call['function']['arguments']})")
                        
                        result = execute_tool_call(tool_call)
                        print(f"✓ 工具执行结果: {result[:100]}{'...' if len(result) > 100 else ''}")
                        
                        # 添加工具结果消息
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": result
                        })
                    
                    # 再次调用 API 获取最终回复
                    response = call_api(messages)
                    final_message = response["choices"][0]["message"]
                    messages.append(final_message)
                    
                    print(f"\n💬 模型回复:\n{final_message['content']}")
                else:
                    # 直接回复
                    messages.append(message)
                    print(f"\n💬 模型回复:\n{message['content']}")
                    
            except Exception as e:
                print(f"\n❌ API 错误: {e}")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except EOFError:
            print("\n\n👋 再见！")
            break
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
