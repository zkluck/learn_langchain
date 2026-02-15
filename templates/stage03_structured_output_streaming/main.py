"""Stage 03: 结构化输出 + 流式输出示例。"""

import os

from langchain.agents import create_agent
from pydantic import BaseModel, Field


# 用 Pydantic 定义你希望模型输出的固定结构。
class TicketResult(BaseModel):
    category: str = Field(description="工单分类")
    priority: str = Field(description="优先级，例如 P1/P2/P3")
    reason: str = Field(description="分类原因")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    # response_format=TicketResult 会要求输出符合该 schema。
    agent = create_agent(
        model="openai:gpt-4.1-mini",
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
    print("Structured:", result)

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
        print(event)
