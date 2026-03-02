#!/usr/bin/env python3
"""
Stage 09: 完整示例汇总
集成所有功能的完整 agentic loop 实现
"""

import glob
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dotenv import load_dotenv

Message = Dict[str, Any]
ToolSchema = Dict[str, Any]
ToolCall = Dict[str, Any]

WORKSPACE_ROOT = Path.cwd().resolve()
MAX_TOOL_ROUNDS = 8
MAX_TOOL_RESULT_PREVIEW = 200
MAX_TOOL_OUTPUT_CHARS = 8000

# 预加载 .env 文件以便后续读取 API Key 等配置
load_dotenv()


def configure_stdio() -> None:
    """保留终端编码，仅放宽错误处理，避免中文/emoji 输出报错"""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="replace")
            except OSError:
                # 某些终端不支持重设参数，忽略即可
                pass


def normalize_base_url(base_url: str) -> str:
    """兼容两种地址写法：.../v1 或 .../chat/completions"""
    url = base_url.strip().rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/v1"):
        return f"{url}/chat/completions"
    return url


def normalize_model(model: str) -> str:
    """兼容历史写法 openai:qwen3-max -> qwen3-max"""
    value = model.strip()
    if value.startswith("openai:"):
        return value.split(":", 1)[1]
    return value


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


# 工具实现
def read_tool(file_path: str) -> str:
    """读取文件内容并添加行号"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
    if not path.exists():
        return f"错误: 文件 '{file_path}' 不存在"

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return f"错误: 读取文件失败 - {error}"

    if not lines:
        return "(空文件)"

    numbered_lines = [f"{idx}: {line}" for idx, line in enumerate(lines, 1)]
    return "\n".join(numbered_lines)


def write_tool(file_path: str, content: str) -> str:
    """将内容写入文件"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"错误: 写入文件失败 - {error}"

    return f"[OK] 成功写入文件: {to_workspace_relative(path)}"


def edit_tool(file_path: str, old_text: str, new_text: str) -> str:
    """编辑文件内容"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
    if not path.exists():
        return f"错误: 文件 '{file_path}' 不存在"

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        return f"错误: 读取文件失败 - {error}"

    if old_text not in content:
        return "错误: 在文件中未找到要替换的文本"

    try:
        path.write_text(content.replace(old_text, new_text), encoding="utf-8")
    except OSError as error:
        return f"错误: 编辑文件失败 - {error}"

    return f"[OK] 成功编辑文件: {to_workspace_relative(path)}"


def glob_tool(pattern: str) -> str:
    """使用 glob 模式搜索文件"""
    try:
        matches: List[str] = []
        for raw_match in glob.glob(pattern, recursive=True):
            path = Path(raw_match)
            if not is_in_workspace(path):
                continue
            matches.append(to_workspace_relative(path))
        if not matches:
            return f"未找到匹配 '{pattern}' 的文件"
        preview = "\n".join(matches[:20])
        suffix = "\n..." if len(matches) > 20 else ""
        return f"找到 {len(matches)} 个文件:\n{preview}{suffix}"
    except Exception as error:
        return f"错误: 搜索文件失败 - {error}"


def grep_tool(pattern: str, file_pattern: str = "*") -> str:
    """在文件中搜索文本模式"""
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        return f"错误: 无效正则表达式 - {error}"

    try:
        matches: List[str] = []
        for file_path in glob.glob(file_pattern, recursive=True):
            path = Path(file_path)
            if not path.is_file() or not is_in_workspace(path):
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                # 跳过无法读取的文件
                continue
            for idx, line in enumerate(lines, 1):
                if compiled.search(line):
                    relative_path = to_workspace_relative(path)
                    matches.append(f"{relative_path}:{idx}: {line}")
            if len(matches) >= 50:
                break

        if not matches:
            return f"未找到匹配模式 '{pattern}' 的内容"

        preview = "\n".join(matches[:20])
        suffix = "\n..." if len(matches) > 20 else ""
        return f"找到 {len(matches)} 个匹配:\n{preview}{suffix}"
    except Exception as error:
        return f"错误: 搜索内容失败 - {error}"


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
        return "错误: 命令执行超时 (30秒)"
    except OSError as error:
        return f"错误: 执行命令失败 - {error}"

    output: List[str] = []
    if result.stdout.strip():
        output.append(f"输出:\n{clip_text(result.stdout)}")
    if result.stderr.strip():
        output.append(f"错误:\n{clip_text(result.stderr)}")
    output.append(f"退出码: {result.returncode}")
    return "\n".join(output)


# 工具定义和 schema
TOOLS: Dict[str, Dict[str, Any]] = {
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
                    "description": "要写入的内容",
                },
            },
            "required": ["file_path", "content"],
        },
    },
    "edit": {
        "description": "编辑文件内容，替换指定文本",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要编辑的文件路径（必须在当前工作目录内）",
                },
                "old_text": {
                    "type": "string",
                    "description": "要被替换的文本",
                },
                "new_text": {
                    "type": "string",
                    "description": "替换后的新文本",
                },
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
                    "description": "glob 搜索模式，如 *.py",
                }
            },
            "required": ["pattern"],
        },
    },
    "grep": {
        "description": "在文件中搜索文本模式",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "要搜索的正则表达式模式",
                },
                "file_pattern": {
                    "type": "string",
                    "description": "文件搜索模式，默认为 *",
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


def make_schema() -> List[ToolSchema]:
    """生成工具的 JSON schema"""
    tools: List[ToolSchema] = []
    for name, tool in TOOLS.items():
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
        )
    return tools


# API 调用
def call_api(messages: List[Message], tools: Optional[List[ToolSchema]] = None) -> Dict[str, Any]:
    """调用 DashScope API"""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = normalize_base_url(
        os.getenv(
            "OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        )
    )
    model = normalize_model(os.getenv("MODEL", "qwen3-max"))

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 环境变量未设置")

    # 构造请求数据
    data: Dict[str, Any] = {
        "model": model,
        "messages": messages,
    }

    if tools:
        data["tools"] = tools
        data["tool_choice"] = "auto"

    # 发送请求
    req = urllib.request.Request(
        base_url,
        data=json.dumps(data).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        error_msg = f"HTTP {error.code}: {error.reason}"
        try:
            error_detail = json.loads(error.read().decode("utf-8"))
            message = error_detail.get("error", {}).get("message", "")
            if message:
                error_msg += f" - {message}"
        except Exception:
            pass
        raise RuntimeError(error_msg)
    except urllib.error.URLError as error:
        raise RuntimeError(f"网络错误: {error.reason}")
    except Exception as error:
        raise RuntimeError(f"API 调用失败: {error}")


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


# 工具执行
def execute_tool_call(tool_call: ToolCall) -> str:
    """执行工具调用"""
    function = tool_call.get("function")
    if not isinstance(function, dict):
        return "错误: tool_call 结构不正确"
    function_name = function.get("name")
    if not isinstance(function_name, str) or not function_name:
        return "错误: 缺少工具名称"

    try:
        arguments = parse_tool_arguments(function.get("arguments", {}))
    except (ValueError, json.JSONDecodeError) as error:
        return f"错误: 无法解析工具参数 - {error}"

    tool_functions: Dict[str, Callable[..., str]] = {
        "read": read_tool,
        "write": write_tool,
        "edit": edit_tool,
        "glob": glob_tool,
        "grep": grep_tool,
        "bash": bash_tool,
    }

    executor = tool_functions.get(function_name)
    if executor is None:
        return f"错误: 未知工具 '{function_name}'"

    try:
        return executor(**arguments)
    except TypeError as error:
        return f"错误: 参数缺失或格式不正确 - {error}"
    except Exception as error:
        return f"工具执行失败: {error}"


# 主循环
def main() -> int:
    """主函数：交互式代理循环"""
    configure_stdio()
    print("=== nanocode_dashscope Stage 09: 完整代理 ===\n")

    # 检查环境变量
    if not os.getenv("OPENAI_API_KEY"):
        print("错误: OPENAI_API_KEY 环境变量未设置")
        return 1

    if os.getenv("ENABLE_BASH_TOOL", "0") != "1":
        print("[INFO] 为安全起见，bash 工具默认关闭（可设置 ENABLE_BASH_TOOL=1 开启）")

    messages: List[Message] = []
    tools_schema = make_schema()

    print("[INFO] 输入你的问题 (输入 /c 清空历史, /q 退出):")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n[INFO] 再见！")
            break

        if user_input == "/q":
            print("\n[INFO] 再见！")
            break
        if user_input == "/c":
            messages = []
            print("\n[OK] 对话历史已清空")
            continue
        if not user_input:
            continue

        # 添加用户消息
        messages.append({"role": "user", "content": user_input})

        # 调用 API
        try:
            response = call_api(messages, tools_schema)
        except RuntimeError as error:
            print(f"\n[ERR] API 错误: {error}")
            messages.pop()
            continue

        reached_tool_limit = True
        for _ in range(MAX_TOOL_ROUNDS):
            try:
                message = extract_assistant_message(response)
            except RuntimeError as error:
                print(f"\n[ERR] 响应解析失败: {error}")
                reached_tool_limit = False
                break

            messages.append(message)
            tool_calls = message.get("tool_calls")

            # 处理工具调用
            if not isinstance(tool_calls, list) or not tool_calls:
                print(f"\n[ASSISTANT] 模型回复:\n{message.get('content', '(无内容)')}")
                reached_tool_limit = False
                break

            # 执行每个工具调用
            for tool_call in tool_calls:
                function = tool_call.get("function", {})
                tool_name = function.get("name", "unknown") if isinstance(function, dict) else "unknown"
                args_preview = function.get("arguments", "{}") if isinstance(function, dict) else "{}"
                print(f"\n[TOOL] 调用工具: {tool_name}({args_preview})")

                result = execute_tool_call(tool_call)
                preview = result if len(result) <= MAX_TOOL_RESULT_PREVIEW else f"{result[:MAX_TOOL_RESULT_PREVIEW]}..."
                print(f"[OK] 工具执行结果: {preview}")

                # 添加工具结果消息
                tool_call_id = tool_call.get("id")
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(tool_call_id) if tool_call_id else "",
                        "content": result,
                    }
                )

            # 再次调用 API 获取后续回复（可能继续调用工具）
            try:
                response = call_api(messages, tools_schema)
            except RuntimeError as error:
                print(f"\n[ERR] API 错误: {error}")
                reached_tool_limit = False
                break

        if reached_tool_limit:
            print(f"\n[ERR] 工具调用轮次超过上限（{MAX_TOOL_ROUNDS} 轮），已停止当前请求。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
