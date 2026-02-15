"""终端友好的 Agent 结果打印工具。"""

from __future__ import annotations

from typing import Any


def _as_text(value: Any) -> str:
    """把不同类型的 content 统一转成可读文本。"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _print_usage(prefix: str, response_metadata: dict[str, Any], usage_metadata: dict[str, Any]) -> None:
    """打印 token 使用信息（如果有）。"""
    token_usage = response_metadata.get("token_usage", {})
    total = token_usage.get("total_tokens") or usage_metadata.get("total_tokens")
    prompt = token_usage.get("prompt_tokens") or usage_metadata.get("input_tokens")
    completion = token_usage.get("completion_tokens") or usage_metadata.get("output_tokens")

    if total is not None:
        print(f"   {prefix}tokens: prompt={prompt}, completion={completion}, total={total}")


def pretty_print_agent_result(result: dict[str, Any], title: str = "Agent 执行结果") -> None:
    """打印 Human/AI/Tool 的核心返回值，便于新手理解执行轨迹。"""
    messages = result.get("messages", [])
    if not messages:
        print(f"\n[{title}] 没有可显示的消息。")
        return

    print(f"\n================ {title} ================\n")

    for index, message in enumerate(messages, start=1):
        message_type = getattr(message, "type", message.__class__.__name__)
        message_id = getattr(message, "id", None)
        content = _as_text(getattr(message, "content", ""))

        if message_type == "human":
            print(f"{index}. HumanMessage")
            if message_id:
                print(f"   id: {message_id}")
            print(f"   content: {content}\n")
            continue

        if message_type == "ai":
            print(f"{index}. AIMessage")
            if message_id:
                print(f"   id: {message_id}")

            response_metadata = getattr(message, "response_metadata", {}) or {}
            usage_metadata = getattr(message, "usage_metadata", {}) or {}
            model_name = response_metadata.get("model_name")
            finish_reason = response_metadata.get("finish_reason")

            if model_name:
                print(f"   model: {model_name}")
            if finish_reason:
                print(f"   finish_reason: {finish_reason}")

            _print_usage(prefix="", response_metadata=response_metadata, usage_metadata=usage_metadata)

            tool_calls = getattr(message, "tool_calls", []) or []
            if tool_calls:
                print("   tool_calls:")
                for call in tool_calls:
                    call_id = call.get("id")
                    name = call.get("name", "unknown_tool")
                    args = call.get("args", {})
                    print(f"   - id={call_id}, name={name}, args={args}")
                print()
            else:
                print(f"   content: {content}\n")
            continue

        if message_type == "tool":
            print(f"{index}. ToolMessage")
            if message_id:
                print(f"   id: {message_id}")

            tool_name = getattr(message, "name", "unknown_tool")
            tool_call_id = getattr(message, "tool_call_id", None)
            print(f"   tool_name: {tool_name}")
            if tool_call_id:
                print(f"   tool_call_id: {tool_call_id}")
            print(f"   content: {content}\n")
            continue

        # 兜底：未知消息类型直接打印核心字段。
        print(f"{index}. {message.__class__.__name__}")
        if message_id:
            print(f"   id: {message_id}")
        print(f"   content: {content}\n")

    print("============================================\n")


def pretty_print_stream_event(event: Any) -> None:
    """简洁打印流式事件。"""
    if isinstance(event, dict):
        keys = list(event.keys())
        print(f"- event keys: {keys}")

        # 如果有 messages，打印最后一条的类型与内容预览。
        messages = event.get("messages")
        if isinstance(messages, list) and messages:
            last = messages[-1]
            mtype = getattr(last, "type", last.__class__.__name__)
            content = _as_text(getattr(last, "content", ""))
            preview = content[:120].replace("\n", " ")
            print(f"  last_message: type={mtype}, preview={preview}")
    else:
        print(f"- event: {event}")
