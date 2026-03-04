#!/usr/bin/env python3
"""
Stage 10: 使用 LangGraph 实现完整代理
在 Stage 09 手写循环基础上，改为 Graph + ToolNode 实现工具调用。
"""

import glob
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# 说明：工作区根目录等于脚本启动目录。
# 所有文件工具都必须限制在这个目录内，避免模型误操作系统其它路径。
WORKSPACE_ROOT = Path.cwd().resolve()

# 与 Stage 09 保持一致：最多允许 8 轮工具调用。
MAX_TOOL_ROUNDS = 8

# 图内部是“模型节点 + 工具节点”交替执行。
# 一轮工具调用通常至少消耗 2 次递归（模型一次、工具一次），因此这里做倍数放大。
GRAPH_RECURSION_LIMIT = MAX_TOOL_ROUNDS * 2 + 4

# 输出保护：避免终端被超长工具结果刷屏。
MAX_TOOL_RESULT_PREVIEW = 200
MAX_TOOL_OUTPUT_CHARS = 8000


def configure_stdio() -> None:
    """保留终端编码，仅放宽错误处理，避免中文/emoji 输出报错。"""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="replace")
            except OSError:
                # 少量终端不支持 reconfigure，忽略即可，不影响主流程。
                pass


def normalize_model(model: str) -> str:
    """兼容历史写法 openai:qwen3-max -> qwen3-max。"""
    value = model.strip()
    if value.startswith("openai:"):
        return value.split(":", 1)[1]
    return value


def normalize_base_url_for_sdk(base_url: str) -> str:
    """把 chat/completions 形式转换为 OpenAI SDK 需要的 base_url（.../v1）。"""
    url = base_url.strip().rstrip("/")
    if url.endswith("/chat/completions"):
        return url[: -len("/chat/completions")]
    if url.endswith("/v1"):
        return url
    # 若用户给的是其它自定义网关路径，保持原样，让 SDK 继续尝试。
    return url


def resolve_workspace_path(file_path: str) -> Path:
    """将路径限制在当前工作目录内，防止越界访问。"""
    raw_path = Path(file_path)
    resolved = raw_path.resolve() if raw_path.is_absolute() else (WORKSPACE_ROOT / raw_path).resolve()
    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as error:
        raise ValueError(f"路径越界: '{file_path}' 不在工作目录内") from error
    return resolved


def is_in_workspace(path: Path) -> bool:
    """判断路径是否位于工作目录内。"""
    try:
        path.resolve().relative_to(WORKSPACE_ROOT)
        return True
    except ValueError:
        return False


def to_workspace_relative(path: Path) -> str:
    """将绝对路径转换为相对工作目录路径，便于阅读。"""
    try:
        return str(path.resolve().relative_to(WORKSPACE_ROOT))
    except ValueError:
        return str(path)


def clip_text(text: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    """限制输出长度，避免工具返回过大文本。"""
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[:limit]}\n...(已截断 {len(stripped) - limit} 字符)"


def read_impl(file_path: str) -> str:
    """读取文件内容并附带行号。"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
    if not path.exists():
        return f"错误: 文件 '{file_path}' 不存在"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        return f"错误: 读取失败 - {error}"
    if not lines:
        return "(空文件)"
    numbered = [f"{idx}: {line}" for idx, line in enumerate(lines, 1)]
    return "\n".join(numbered)


def write_impl(file_path: str, content: str) -> str:
    """写入文本至指定文件。"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"错误: 写入失败 - {error}"
    return f"[OK] 写入文件: {to_workspace_relative(path)}"


def edit_impl(file_path: str, old_text: str, new_text: str) -> str:
    """在文件中替换文本。"""
    try:
        path = resolve_workspace_path(file_path)
    except ValueError as error:
        return f"错误: {error}"
    if not path.exists():
        return f"错误: 文件 '{file_path}' 不存在"
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        return f"错误: 读取失败 - {error}"
    if old_text not in content:
        return "错误: 未找到要替换的文本"
    try:
        path.write_text(content.replace(old_text, new_text), encoding="utf-8")
    except OSError as error:
        return f"错误: 编辑失败 - {error}"
    return f"[OK] 成功替换文本: {old_text} -> {new_text}"


def glob_impl(pattern: str) -> str:
    """使用 glob 搜索文件。"""
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


def grep_impl(pattern: str, file_pattern: str = "*") -> str:
    """在文件中查找正则匹配。"""
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        return f"错误: 无效正则表达式 - {error}"

    results: List[str] = []
    for file_path in glob.glob(file_pattern, recursive=True):
        path = Path(file_path)
        if not path.is_file() or not is_in_workspace(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for idx, line in enumerate(lines, 1):
            if compiled.search(line):
                results.append(f"{to_workspace_relative(path)}:{idx}: {line}")
        if len(results) >= 50:
            break
    if not results:
        return f"未找到包含 '{pattern}' 的内容"
    preview = "\n".join(results[:20])
    suffix = "\n..." if len(results) > 20 else ""
    return f"找到 {len(results)} 处匹配:\n{preview}{suffix}"


def bash_impl(command: str) -> str:
    """执行命令并返回输出/错误/退出码（默认关闭）。"""
    if os.getenv("ENABLE_BASH_TOOL", "0") != "1":
        return "错误: bash 工具默认关闭，请设置 ENABLE_BASH_TOOL=1 后重试"
    if not command.strip():
        return "错误: 命令不能为空"
    try:
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


# 使用 LangChain 的 @tool 装饰器注册工具。
# 注意：这里显式指定 tool name，确保与 Stage 09 名称保持一致（read/write/edit/glob/grep/bash）。
@tool("read")
def read_tool(file_path: str) -> str:
    """读取文件内容并显示行号。参数 file_path 必须在当前工作目录内。"""
    return read_impl(file_path)


@tool("write")
def write_tool(file_path: str, content: str) -> str:
    """将文本写入文件。参数 file_path 必须在当前工作目录内。"""
    return write_impl(file_path, content)


@tool("edit")
def edit_tool(file_path: str, old_text: str, new_text: str) -> str:
    """在文件中执行字符串替换。参数 file_path 必须在当前工作目录内。"""
    return edit_impl(file_path, old_text, new_text)


@tool("glob")
def glob_tool(pattern: str) -> str:
    """按 glob 模式查找文件，例如 **/*.py。"""
    return glob_impl(pattern)


@tool("grep")
def grep_tool(pattern: str, file_pattern: str = "*") -> str:
    """按正则在文件中搜索内容，file_pattern 默认 *。"""
    return grep_impl(pattern, file_pattern)


@tool("bash")
def bash_tool(command: str) -> str:
    """执行命令（默认关闭，需设置 ENABLE_BASH_TOOL=1）。"""
    return bash_impl(command)


def build_graph() -> Any:
    """构建 LangGraph：model -> (tools?) -> model ... -> END。"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    model_name = normalize_model(os.getenv("MODEL", "qwen3-max"))
    base_url = normalize_base_url_for_sdk(
        os.getenv(
            "OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        )
    )

    # ChatOpenAI 使用 OpenAI 兼容协议；DashScope 兼容接口可直接复用。
    model = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        timeout=60,
    )
    tools = [read_tool, write_tool, edit_tool, glob_tool, grep_tool, bash_tool]
    model_with_tools = model.bind_tools(tools)
    tool_node = ToolNode(tools)

    def call_model(state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """模型节点：读取消息历史并生成下一条 AIMessage。"""
        response = model_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition, {"tools": "tools", END: END})
    builder.add_edge("tools", "model")
    return builder.compile()


def content_to_text(content: Any) -> str:
    """将 LangChain 消息 content 统一转换成可打印文本。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: List[str] = []
        for item in content:
            if isinstance(item, str):
                chunks.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if text is not None:
                    chunks.append(str(text))
        return "\n".join(chunks)
    return str(content)


def sanitize_input_text(text: str) -> str:
    """清理非法代理项字符，避免请求编码时抛出 UnicodeError。"""
    try:
        return text.encode("utf-8", errors="replace").decode("utf-8")
    except Exception:
        return text


def format_tool_args(args: Any) -> str:
    """把 tool args 转成稳定字符串，便于日志展示。"""
    if isinstance(args, dict):
        try:
            return json.dumps(args, ensure_ascii=False)
        except Exception:
            return str(args)
    return str(args)


def print_incremental_messages(new_messages: Sequence[BaseMessage]) -> None:
    """打印本轮新增消息：先打印工具调用过程，再打印最终 assistant 回复。"""
    assistant_text = ""
    for message in new_messages:
        if isinstance(message, AIMessage):
            tool_calls = message.tool_calls or []
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = str(tool_call.get("name", "unknown"))
                    args_text = format_tool_args(tool_call.get("args", {}))
                    print(f"\n[TOOL] 调用工具: {tool_name}({args_text})")
                continue
            text = content_to_text(message.content).strip()
            if text:
                assistant_text = text
            continue

        if isinstance(message, ToolMessage):
            result = content_to_text(message.content)
            preview = result if len(result) <= MAX_TOOL_RESULT_PREVIEW else f"{result[:MAX_TOOL_RESULT_PREVIEW]}..."
            print(f"[OK] 工具执行结果: {preview}")

    if assistant_text:
        print(f"\n[ASSISTANT] 模型回复:\n{assistant_text}")
    else:
        print("\n[ASSISTANT] 模型回复:\n(无内容)")


def main() -> int:
    """交互式入口：保留 /q /c 命令，外部行为与 Stage 09 基本一致。"""
    configure_stdio()
    print("=== nanocode_dashscope Stage 10: LangGraph 完整代理 ===\n")

    if not os.getenv("OPENAI_API_KEY"):
        print("错误: OPENAI_API_KEY 环境变量未设置")
        return 1
    if os.getenv("ENABLE_BASH_TOOL", "0") != "1":
        print("[INFO] 为安全起见，bash 工具默认关闭（可设置 ENABLE_BASH_TOOL=1 开启）")

    try:
        graph = build_graph()
    except Exception as error:
        print(f"错误: 图构建失败 - {error}")
        return 1

    messages: List[BaseMessage] = []
    print("[INFO] 输入你的问题 (输入 /c 清空历史, /q 退出):")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] 再见！")
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

        user_message = HumanMessage(content=sanitize_input_text(user_input))
        input_messages = messages + [user_message]

        try:
            # recursion_limit 是 LangGraph 的回路保护开关。
            # 达到阈值时会抛 GraphRecursionError，避免无限工具调用。
            result = graph.invoke(
                {"messages": input_messages},
                config={"recursion_limit": GRAPH_RECURSION_LIMIT},
            )
        except GraphRecursionError:
            print(f"\n[ERR] 工具调用轮次超过上限（{MAX_TOOL_ROUNDS} 轮），已停止当前请求。")
            continue
        except Exception as error:
            print(f"\n[ERR] 调用失败: {error}")
            continue

        result_messages = result.get("messages")
        if not isinstance(result_messages, list):
            print("\n[ERR] 响应格式异常: 缺少 messages")
            continue

        new_messages = result_messages[len(input_messages):]
        print_incremental_messages(new_messages)
        messages = result_messages

    return 0


if __name__ == "__main__":
    # 预加载 .env，便于读取 OPENAI_API_KEY / OPENAI_BASE_URL / MODEL 等配置。
    load_dotenv()
    raise SystemExit(main())
