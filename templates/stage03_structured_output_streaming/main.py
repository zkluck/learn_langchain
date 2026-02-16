"""Stage 03: 结构化输出 + 流式输出示例。"""

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from templates.common.pretty_print import pretty_print_agent_result as _pretty_print_agent_result, pretty_print_stream_event as _pretty_print_stream_event
from pydantic import BaseModel, Field


# 用 Pydantic 定义你希望模型输出的固定结构。
class TicketResult(BaseModel):
    category: str = Field(description="工单分类")
    priority: str = Field(description="优先级，例如 P1/P2/P3")
    reason: str = Field(description="分类原因")


def pretty_print_agent_result(result: dict[str, Any], title: str = "Agent 执行结果") -> None:
    """调用公共打印工具，展示消息核心返回值。"""
    _pretty_print_agent_result(result=result, title=title)


def pretty_print_stream_event(event: Any) -> None:
    """调用公共打印工具，展示流式事件核心信息。"""
    _pretty_print_stream_event(event)


def _extract_chunk_text(chunk: Any) -> str:
    """把 stream_mode='messages' 返回的 chunk 尽量转成文本。"""
    content = getattr(chunk, "content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
                continue

            text = getattr(block, "text", None)
            if isinstance(text, str):
                parts.append(text)
        return "".join(parts)

    return ""

if __name__ == "__main__":
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    # response_format=TicketResult 会要求输出符合该 schema。
    agent = create_agent(
        model="openai:qwen3-max",
        tools=[],
        system_prompt="你是工单分类助手。",
        response_format=TicketResult,
    )

    # 1) 结构化输出：返回对象中会包含结构化结果。
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "用户反馈：支付后页面报500错误，无法继续下单。",
                }
            ]
        }
    )
    pretty_print_agent_result(result, title="Structured Output")

    # 2) 流式输出：用 stream_mode="messages" 打印 token/chunk。
    # 说明：response_format 常会走 tool_call，更新事件可能只在结束时返回一次。
    # 为了更直观看到“逐步输出”，这里单独创建一个纯文本流式 Agent。
    stream_agent = create_agent(
        model="openai:qwen3-max",
        tools=[],
        system_prompt="你是运维助手，请对输入做简短总结。",
    )

    print("Streaming tokens:", end=" ", flush=True)
    saw_token = False
    for chunk, _metadata in stream_agent.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请总结：今天订单接口错误率升高。",
                }
            ]
        },
        stream_mode="messages",
    ):
        text = _extract_chunk_text(chunk)
        if text:
            print(text, end="", flush=True)
            saw_token = True

    if not saw_token:
        print("(当前模型未返回可见的增量 token)")
    else:
        print()
