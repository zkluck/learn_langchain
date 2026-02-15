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

    # 2) 流式输出：逐步返回更新事件，适合实时展示。
    # 不同模型提供方的事件结构可能略有差异。
    print("Streaming events:")
    for event in agent.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请总结：今天订单接口错误率升高。",
                }
            ]
        },
        stream_mode="updates",
    ):
        pretty_print_stream_event(event)
