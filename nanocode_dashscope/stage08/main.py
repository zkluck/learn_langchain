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
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List
from dotenv import load_dotenv

Message = Dict[str, Any]
ToolSchema = Dict[str, Any]
ToolCall = Dict[str, Any]

# 当前脚本默认将“启动目录”作为工作区根路径。
# 后续 read/write/edit/glob/grep/bash 都会基于该目录执行，避免误操作到其它目录。
WORKSPACE_ROOT = Path.cwd().resolve()

# 工具调用最多连续回合数：避免模型陷入“无限调用工具”的死循环。
MAX_TOOL_ROUNDS = 8

# 终端里打印工具结果时只展示前缀，避免刷屏。
MAX_TOOL_RESULT_PREVIEW = 200

# 工具真实返回给模型的文本也要限制长度，防止上下文爆炸。
MAX_TOOL_OUTPUT_CHARS = 8000

# 预加载 .env 文件以便后续读取 API Key 等配置
load_dotenv()


def configure_stdio() -> None:
    """保留终端编码，仅放宽错误处理，避免中文/emoji 输出报错"""
    # 不强制改编码，只把不可编码字符替换掉，兼容 Windows/Powershell 各种终端设置。
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
        # 用户常把 OPENAI_BASE_URL 配成根路径，这里自动补全到 chat/completions。
        return f"{url}/chat/completions"
    return url


def normalize_model(model: str) -> str:
    """兼容历史写法 openai:qwen3-max -> qwen3-max"""
    value = model.strip()
    if value.startswith("openai:"):
        # 早期示例用了 openai: 前缀，这里兼容为 DashScope 可识别模型名。
        return value.split(":", 1)[1]
    return value


def resolve_workspace_path(file_path: str) -> Path:
    """将路径限制在当前工作目录内，防止越界访问"""
    raw_path = Path(file_path)
    # 相对路径按工作区拼接；绝对路径保持原样后再做越界校验。
    resolved = raw_path.resolve() if raw_path.is_absolute() else (WORKSPACE_ROOT / raw_path).resolve()
    try:
        # 关键安全检查：必须是 WORKSPACE_ROOT 的子路径。
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
        # 正常情况下不会走到这里；兜底返回原路径，避免格式化报错。
        return str(path)


def clip_text(text: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    """限制输出长度，避免工具返回过大文本"""
    # strip 后再判断长度，避免纯空白内容占用配额。
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
            # 忽略不可读文件，继续扫其它文件。
            continue
        if len(results) >= 50:
            # 上限保护：匹配太多会占满上下文，截断即可。
            break
    if not results:
        return f"未找到包含 '{pattern}' 的内容"
    preview = "\n".join(results[:20])
    suffix = "\n..." if len(results) > 20 else ""
    return f"找到 {len(results)} 处匹配:\n{preview}{suffix}"


def bash_tool(command: str) -> str:
    """执行命令并返回输出/错误/退出码（默认关闭）"""
    if os.getenv("ENABLE_BASH_TOOL", "0") != "1":
        # 默认关掉高风险能力，只有显式开启才允许执行。
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
            # 强制在工作区运行，避免模型把命令切到系统敏感目录。
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
    # 这里维护“工具单一事实来源”：函数名、描述、参数结构都在这里定义。
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
    base_url = normalize_base_url(
        os.getenv(
            "OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        )
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    # messages 必须携带完整上下文（用户 + assistant + tool），模型才能“记住历史”。
    payload: Dict[str, Any] = {
        "model": normalize_model(os.getenv("MODEL", "qwen3-max")),
        "messages": messages,
    }
    if tools:
        # 附加工具定义并切换到自动工具模式
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    # 直接用 urllib 发 POST，便于教学阶段观察原始请求结构。
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
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "")
            body_text = response.read().decode("utf-8", errors="replace").strip()

            if not body_text:
                raise RuntimeError(
                    f"HTTP {status}: 响应体为空 (Content-Type: {content_type or 'unknown'})"
                )

            try:
                parsed = json.loads(body_text)
            except json.JSONDecodeError as error:
                preview = body_text[:400]
                raise RuntimeError(
                    f"HTTP {status}: 响应不是有效 JSON (Content-Type: {content_type or 'unknown'})\n"
                    f"解析错误: {error}\n"
                    f"响应预览:\n{preview}"
                )

            if not isinstance(parsed, dict):
                raise RuntimeError(f"HTTP {status}: 响应 JSON 顶层类型异常: {type(parsed).__name__}")
            return parsed
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8") if error.fp else ""
        raise RuntimeError(f"HTTP {error.code}: {error.reason}\n{detail}")
    except urllib.error.URLError as error:
        raise RuntimeError(f"网络错误: {error.reason}")


def extract_assistant_message(response: Dict[str, Any]) -> Message:
    """从 API 响应中提取 assistant message，并做结构校验"""
    # 做结构校验而不是直接 response["choices"][0]["message"]，
    # 可以在返回格式变化时给出更友好的错误。
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
        # 某些模型会把 arguments 作为 JSON 字符串返回，需要反序列化。
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
        # 通过 **arguments 动态分发参数，让 schema 与执行器保持对齐。
        return executor(**arguments)
    except TypeError as error:
        return f"错误: 参数缺失或格式不正确 - {error}"
    except Exception as error:
        return f"错误: 工具执行失败 - {error}"


def main() -> int:
    """带工具调用的命令行循环"""
    configure_stdio()
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

        # 第 1 步：先把用户问题写入上下文。
        messages.append({"role": "user", "content": user_input})

        try:
            # 第 2 步：首次请求模型，模型可能直接回答，也可能返回 tool_calls。
            response = call_api(messages, schemas)
        except RuntimeError as error:
            print(f"\n[ERR] 调用失败: {error}")
            # 本轮失败则回滚最后一条 user 消息，避免脏上下文影响后续轮次。
            messages.pop()
            continue

        # 进入“工具循环”：assistant -> tool -> assistant ... 直到 assistant 给出最终自然语言答案。
        reached_tool_limit = True
        for _ in range(MAX_TOOL_ROUNDS):
            try:
                assistant_message = extract_assistant_message(response)
            except RuntimeError as error:
                print(f"\n[ERR] 响应解析失败: {error}")
                reached_tool_limit = False
                break

            # 无论是否调用工具，都先保存 assistant 消息，保证上下文完整可追溯。
            messages.append(assistant_message)
            tool_calls = assistant_message.get("tool_calls")
            if not isinstance(tool_calls, list) or not tool_calls:
                # 没有工具调用，说明这是最终答复，直接打印并结束当前用户问题。
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
                # 工具结果必须以 role=tool 回传给模型，并带上 tool_call_id 才能正确对齐。
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(tool_call_id) if tool_call_id else "",
                        "content": result,
                    }
                )

            try:
                # 把“assistant 的 tool_calls + tool 执行结果”一起发回模型，请它继续推理。
                response = call_api(messages, schemas)
            except RuntimeError as error:
                print(f"\n[ERR] 调用失败: {error}")
                reached_tool_limit = False
                break

        if reached_tool_limit:
            # 到这里表示连续 MAX_TOOL_ROUNDS 次都没收敛，主动中断防止死循环。
            print(f"\n[ERR] 工具调用轮次超过上限（{MAX_TOOL_ROUNDS} 轮），已停止当前请求。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
