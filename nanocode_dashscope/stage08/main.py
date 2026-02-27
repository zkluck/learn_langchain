#!/usr/bin/env python3
"""
Stage 08: 工具调用循环
在基础对话的基础上，支持 DashScope 返回的 tool_calls
"""

import json
import os
import re
import glob
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Dict, List

Message = Dict[str, str]
ToolSchema = Dict[str, object]
ToolCall = Dict[str, object]


def read_tool(file_path: str) -> str:
    """读取文件内容并附带行号"""
    path = Path(file_path)
    if not path.exists():
        return f"错误: 文件 '{file_path}' 不存在"
    # 逐行读取文本，帮助模型定位具体行号
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return f"错误: 读取失败 - {error}"
    if not lines:
        return "(空文件)"
    numbered = [f"{idx}: {line}" for idx, line in enumerate(lines, 1)]
    return "\n".join(numbered)


def write_tool(file_path: str, content: str) -> str:
    """写入文本至指定文件"""
    path = Path(file_path)
    # 自动创建父目录，避免路径不存在导致失败
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"错误: 写入失败 - {error}"
    return f"✓ 写入文件: {file_path}"


def edit_tool(file_path: str, old_text: str, new_text: str) -> str:
    """在文件中替换文本"""
    path = Path(file_path)
    if not path.exists():
        return f"错误: 文件 '{file_path}' 不存在"
    # 读取全文后进行字符串替换，保证简洁可靠
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        return f"错误: 读取失败 - {error}"
    if old_text not in content:
        return "错误: 未找到要替换的文本"
    path.write_text(content.replace(old_text, new_text), encoding="utf-8")
    return f"✓ 成功替换文本: {old_text} -> {new_text}"


def glob_tool(pattern: str) -> str:
    """使用 glob 搜索文件"""
    # 通过 glob 匹配列出文件，方便模型了解上下文
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        return f"未匹配到 '{pattern}'"
    preview = "\n".join(matches[:20])
    suffix = "\n..." if len(matches) > 20 else ""
    return f"找到 {len(matches)} 个文件:\n{preview}{suffix}"


def grep_tool(pattern: str, file_pattern: str = "*") -> str:
    """在文件中查找正则匹配"""
    results: List[str] = []
    compiled = re.compile(pattern, re.IGNORECASE)
    # 遍历匹配到的文件并逐行搜索
    for file_path in glob.glob(file_pattern, recursive=True):
        path = Path(file_path)
        if not path.is_file():
            continue
        try:
            for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if compiled.search(line):
                    results.append(f"{file_path}:{idx}: {line}")
        except OSError:
            continue
        if len(results) >= 50:
            break
    if not results:
        return f"未找到包含 '{pattern}' 的内容"
    preview = "\n".join(results[:20])
    suffix = "\n..." if len(results) > 20 else ""
    return f"找到 {len(results)} 处匹配:\n{preview}{suffix}"


def bash_tool(command: str) -> str:
    """执行 shell 命令并返回输出/错误/退出码"""
    try:
        # 使用 subprocess 运行命令并捕获输出，限制 30 秒超时
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "错误: 命令执行超时 (30 秒)"
    output_parts: List[str] = []
    if result.stdout.strip():
        output_parts.append(f"输出:\n{result.stdout.strip()}")
    if result.stderr.strip():
        output_parts.append(f"错误:\n{result.stderr.strip()}")
    output_parts.append(f"退出码: {result.returncode}")
    return "\n".join(output_parts)


def make_schema() -> List[ToolSchema]:
    """生成 function calling schema"""
    tools: List[ToolSchema] = []
    definitions: Dict[str, Dict[str, object]] = {
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
                    "file_path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"}
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
                        "description": "glob 搜索模式"
                    }
                },
                "required": ["pattern"]
            }
        },
        "grep": {
            "description": "在文件中搜索正则匹配",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "要匹配的正则表达式"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "指定要搜索的文件 glob 模式",
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
                        "description": "要执行的命令"
                    }
                },
                "required": ["command"]
            }
        }
    }
    for name, meta in definitions.items():
        # 转换为 OpenAI/DashScope 兼容的 function 描述
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": meta["description"],
                "parameters": meta["parameters"],
            },
        })
    return tools


def call_api(messages: List[Message], tools: List[ToolSchema] | None) -> Dict[str, object]:
    """调用 DashScope，并可选传入工具 schema"""
    base_url = os.getenv(
        "OPENAI_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    payload: Dict[str, object] = {
        "model": os.getenv("MODEL", "openai:qwen3-max"),
        "messages": messages,
    }
    if tools:
        # 附加工具定义并切换到自动工具模式
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8") if error.fp else ""
        raise RuntimeError(f"HTTP {error.code}: {error.reason}\n{detail}")
    except urllib.error.URLError as error:
        raise RuntimeError(f"网络错误: {error.reason}")


def execute_tool_call(tool_call: ToolCall) -> str:
    """根据 tool_call 调用对应的本地工具"""
    function = tool_call.get("function")
    if not isinstance(function, dict):
        return "错误: tool_call 结构不正确"
    name = function.get("name")
    raw_arguments = function.get("arguments", "{}")
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError:
        return "错误: 无法解析工具参数"

    tool_map: Dict[str, Callable[..., str]] = {
        "read": lambda: read_tool(**arguments),
        "write": lambda: write_tool(**arguments),
        "edit": lambda: edit_tool(**arguments),
        "glob": lambda: glob_tool(**arguments),
        "grep": lambda: grep_tool(**arguments),
        "bash": lambda: bash_tool(**arguments),
    }

    executor = tool_map.get(str(name))
    if executor is None:
        return f"错误: 未知工具 '{name}'"
    try:
        return executor()
    except TypeError as error:
        return f"错误: 参数缺失或格式不正确 - {error}"


def main() -> int:
    """带工具调用的命令行循环"""
    print("=== nanocode_dashscope Stage 08: 工具调用循环 ===\n")

    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请先设置 OPENAI_API_KEY 环境变量")
        return 1

    messages: List[Message] = []
    schemas = make_schema()
    print("🤖 请输入问题 (输入 /c 清空历史, /q 退出):")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break

        if not user_input:
            continue
        if user_input == "/q":
            print("\n👋 再见！")
            break
        if user_input == "/c":
            messages.clear()
            print("\n🧹 对话历史已清空")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = call_api(messages, schemas)
        except RuntimeError as error:
            print(f"\n❌ 调用失败: {error}")
            messages.pop()
            continue

        assistant_message = response["choices"][0]["message"]
        tool_calls = assistant_message.get("tool_calls")

        if tool_calls:
            messages.append(assistant_message)
            for tool_call in tool_calls:
                print(f"\n🔧 调用工具: {tool_call}")
                result = execute_tool_call(tool_call)
                preview = result if len(result) <= 200 else f"{result[:200]}..."
                print(f"✓ 工具结果: {preview}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", ""),
                    "content": result,
                })
            try:
                follow_up = call_api(messages, None)
            except RuntimeError as error:
                print(f"\n❌ 调用失败: {error}")
                continue
            final_message = follow_up["choices"][0]["message"]
            messages.append(final_message)
            print(f"\n💬 模型回复:\n{final_message.get('content', '(无内容)')}")
        else:
            messages.append(assistant_message)
            print(f"\n💬 模型回复:\n{assistant_message.get('content', '(无内容)')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
