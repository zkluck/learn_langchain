"""Stage 02: 使用 @tool 定义更清晰的工具接口。"""

import os

from langchain.agents import create_agent
from langchain.tools import tool


# 使用 @tool 后，LangChain 会把函数描述和参数暴露给模型。
@tool
def weather(city: str) -> str:
    """查询城市天气。"""
    return f"{city}: 多云，23C"


@tool
def multiply(a: float, b: float) -> float:
    """两个数字相乘。"""
    return a * b


@tool
def classify_priority(text: str) -> str:
    """根据文本判断工单优先级。"""
    if "故障" in text or "崩溃" in text:
        return "P1"
    if "慢" in text or "延迟" in text:
        return "P2"
    return "P3"


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    # 这里一次性注册 3 个工具，方便观察模型如何选择调用。
    agent = create_agent(
        model="openai:gpt-4.1-mini",
        tools=[weather, multiply, classify_priority],
        system_prompt="你是客服助手，回答前可调用最合适的工具。",
    )

    # 用户输入里包含多个任务，模型通常会拆解后分别调用工具。
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "北京天气如何？再帮我把 18.5 乘以 6，并评估“系统崩溃”优先级。",
                }
            ]
        }
    )
    print(result)
