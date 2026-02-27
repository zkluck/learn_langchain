#!/usr/bin/env python3
"""
Stage 08: 工具调用循环
在基础对话的基础上，支持 DashScope 返回的 tool_calls
"""

import glob
import json
import os
import re
import shlex
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List

Message = Dict[str, Any]
ToolSchema = Dict[str, Any]
ToolCall = Dict[str, Any]

WORKSPACE_ROOT = Path.cwd().resolve()
MAX_TOOL_ROUNDS = 8
MAX_TOOL_RESULT_PREVIEW = 200
MAX_TOOL_OUTPUT_CHARS = 8000


def resolve_workspace_path(file_path: str) -> Path:
    """将路径限制在当前工作目录内，防止越界访问"""
    raw_path = Path(file_path)
    resolved = raw_path.resolve() if raw_path.is_absolute() else (WORKSPACE_ROOT / raw_path).resolve()
    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as error:
        raise ValueError(f"路径越界: '{file_path}' 不在工作目录内") from error
    return resolved


def is_in_workspace(path: Path) -> bool:
    """判断路径是否位于工作目录内"""
    try:
        path.resolve().relative_to(WORKSPACE_ROOT)
        return True
    except ValueError:
        return False


def to_workspace_relative(path: Path) -> str:
    """将绝对路径转换为相对工作目录路径，便于阅读"""
    try:
        return str(path.resolve().relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)


def clip_text(text: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    """限制输出长度，避免工具返回过大文本"""
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[:limit]}\n...(已截断 {len(stripped) - limit} 字符)"


def read_tool(file_path: str) -> str:
    """读取文件内容并附带行号"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
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
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
    # 自动创建父目录，避免路径不存在导致失败
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"错误: 写入失败 - {error}"
    return f"[OK] 写入文件: {to_workspace_relative(path)}"


def edit_tool(file_path: str, old_text: str, new_text: str) -> str:
    """在文件中替换文本"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
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
    return f"[OK] 成功替换文本: {old_text} -> {new_text}"


def glob_tool(pattern: str) -> str:
    """使用 glob 搜索文件"""
    # 通过 glob 匹配列出文件，结果仅保留工作目录内的路径
    matched_paths: List[str] = []
    for raw_match in glob.glob(pattern, recursive=True):
        path = Path(raw_match)
        if not is_in_workspace(path):
            continue
        matched_paths.append(to_workspace_relative(path))
    if not matched_paths:
        return f"未匹配到 '{pattern}'"
    preview = "\n".join(matched_paths[:20])
    suffix = "\n..." if len(matched_paths) > 20 else ""
    return f"找到 {len(matched_paths)} 个文件:\n{preview}{suffix}"


def grep_tool(pattern: str, file_pattern: str = "*") -> str:
    """在文件中查找正则匹配"""
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        return f"错误: 无效正则表达式 - {error}"

    results: List[str] = []
    # 遍历匹配到的文件并逐行搜索
    for file_path in glob.glob(file_pattern, recursive=True):
        path = Path(file_path)
        if not path.is_file() or not is_in_workspace(path):
            continue
        try:
            for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if compiled.search(line):
                    relative_path = to_workspace_relative(path)
                    results.append(f"{relative_path}:{idx}: {line}")
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
    """执行命令并返回输出/错误/退出码（默认关闭）"""
    if os.getenv("ENABLE_BASH_TOOL", "0") != "1":
        return "错误: bash 工具默认关闭，请设置 ENABLE_BASH_TOOL=1 后重试"

    if not command.strip():
        return "错误: 命令不能为空"

    try:
        # 使用 shell=False 执行命令，避免命令注入风险
        args = shlex.split(command, posix=(os.name != "nt"))
    except ValueError as error:
        return f"错误: 命令解析失败 - {error}"
    if not args:
        return "错误: 命令不能为空"

    try:
        result = subprocess.run(
            args,
            shell=False,
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return "错误: 命令不存在，请确认命令名是否正确"
    except subprocess.TimeoutExpired:
        return "错误: 命令执行超时 (30 秒)"
    except OSError as error:
        return f"错误: 命令执行失败 - {error}"

    output_parts: List[str] = []
    if result.stdout.strip():
        output_parts.append(f"输出:\n{clip_text(result.stdout)}")
    if result.stderr.strip():
        output_parts.append(f"错误:\n{clip_text(result.stderr)}")
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
                        "description": "要读取的文件路径（必须在当前工作目录内）",
                    }
                },
                "required": ["file_path"],
            },
        },
        "write": {
            "description": "将内容写入文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要写入的文件路径（必须在当前工作目录内）",
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的文本",
                    },
                },
                "required": ["file_path", "content"],
            },
        },
        "edit": {
            "description": "在文件中查找并替换文本",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "old_text": {"type": "string"},
                    "new_text": {"type": "string"},
                },
                "required": ["file_path", "old_text", "new_text"],
            },
        },
        "glob": {
            "description": "使用 glob 模式搜索文件",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "glob 搜索模式",
                    }
                },
                "required": ["pattern"],
            },
        },
        "grep": {
            "description": "在文件中搜索正则匹配",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "要匹配的正则表达式",
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "指定要搜索的文件 glob 模式",
                        "default": "*",
                    },
                },
                "required": ["pattern"],
            },
        },
        "bash": {
            "description": "执行命令（默认关闭，需显式设置 ENABLE_BASH_TOOL=1）",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的命令",
                    }
                },
                "required": ["command"],
            },
        },
    }
    for name, meta in definitions.items():
        # 转换为 OpenAI/DashScope 兼容的 function 描述
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": meta["description"],
                    "parameters": meta["parameters"],
                },
            }
        )
    return tools


def call_api(messages: List[Message], tools: List[ToolSchema] | None) -> Dict[str, Any]:
    """调用 DashScope，并可选传入工具 schema"""
    base_url = os.getenv(
        "OPENAI_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    payload: Dict[str, Any] = {
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


def extract_assistant_message(response: Dict[str, Any]) -> Message:
    """从 API 响应中提取 assistant message，并做结构校验"""
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("响应格式异常: 缺少 choices")
    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise RuntimeError("响应格式异常: choice 格式不正确")
    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise RuntimeError("响应格式异常: 缺少 message")
    return message


def parse_tool_arguments(raw_arguments: Any) -> Dict[str, Any]:
    """兼容 string/dict 两种参数格式，统一解析为 dict"""
    if isinstance(raw_arguments, dict):
        return raw_arguments
    if isinstance(raw_arguments, str):
        if not raw_arguments.strip():
            return {}
        parsed = json.loads(raw_arguments)
        if not isinstance(parsed, dict):
            raise ValueError("工具参数必须是 JSON 对象")
        return parsed
    raise ValueError("工具参数格式不支持")


def execute_tool_call(tool_call: ToolCall) -> str:
    """根据 tool_call 调用对应的本地工具"""
    function = tool_call.get("function")
    if not isinstance(function, dict):
        return "错误: tool_call 结构不正确"
    name = function.get("name")
    if not isinstance(name, str) or not name:
        return "错误: 缺少工具名称"

    try:
        arguments = parse_tool_arguments(function.get("arguments", {}))
    except (ValueError, json.JSONDecodeError) as error:
        return f"错误: 无法解析工具参数 - {error}"

    tool_map: Dict[str, Callable[..., str]] = {
        "read": read_tool,
        "write": write_tool,
        "edit": edit_tool,
        "glob": glob_tool,
        "grep": grep_tool,
        "bash": bash_tool,
    }

    executor = tool_map.get(name)
    if executor is None:
        return f"错误: 未知工具 '{name}'"
    try:
        return executor(**arguments)
    except TypeError as error:
        return f"错误: 参数缺失或格式不正确 - {error}"
    except Exception as error:
        return f"错误: 工具执行失败 - {error}"


def main() -> int:
    """带工具调用的命令行循环"""
    print("=== nanocode_dashscope Stage 08: 工具调用循环 ===\n")

    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请先设置 OPENAI_API_KEY 环境变量")
        return 1

    if os.getenv("ENABLE_BASH_TOOL", "0") != "1":
        print("[INFO] 为安全起见，bash 工具默认关闭（可设置 ENABLE_BASH_TOOL=1 开启）")

    messages: List[Message] = []
    schemas = make_schema()
    print("[INFO] 请输入问题 (输入 /c 清空历史, /q 退出):")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] 再见！")
            break

        if not user_input:
            continue
        if user_input == "/q":
            print("\n[INFO] 再见！")
            break
        if user_input == "/c":
            messages.clear()
            print("\n[OK] 对话历史已清空")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = call_api(messages, schemas)
        except RuntimeError as error:
            print(f"\n[ERR] 调用失败: {error}")
            messages.pop()
            continue

        reached_tool_limit = True
        for _ in range(MAX_TOOL_ROUNDS):
            try:
                assistant_message = extract_assistant_message(response)
            except RuntimeError as error:
                print(f"\n[ERR] 响应解析失败: {error}")
                reached_tool_limit = False
                break

            messages.append(assistant_message)
            tool_calls = assistant_message.get("tool_calls")
            if not isinstance(tool_calls, list) or not tool_calls:
                print(f"\n[ASSISTANT] 模型回复:\n{assistant_message.get('content', '(无内容)')}")
                reached_tool_limit = False
                break

            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "unknown") if isinstance(function, dict) else "unknown"
                print(f"\n[TOOL] 调用工具: {tool_name}")
                result = execute_tool_call(tool_call)
                preview = result if len(result) <= MAX_TOOL_RESULT_PREVIEW else f"{result[:MAX_TOOL_RESULT_PREVIEW]}..."
                print(f"[OK] 工具结果: {preview}")
                tool_call_id = tool_call.get("id")
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(tool_call_id) if tool_call_id else "",
                        "content": result,
                    }
                )

            try:
                response = call_api(messages, schemas)
            except RuntimeError as error:
                print(f"\n[ERR] 调用失败: {error}")
                reached_tool_limit = False
                break

        if reached_tool_limit:
            print(f"\n[ERR] 工具调用轮次超过上限（{MAX_TOOL_ROUNDS} 轮），已停止当前请求。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
