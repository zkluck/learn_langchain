"""Stage 01: 观察 Agent 在多轮请求中的工具调用循环。"""

import os

from langchain.agents import create_agent


# 计算工具：把字符串表达式交给 Python 计算。
def calculator(expression: str) -> str:
    """计算数学表达式并返回文本结果。"""
    # 仅用于学习示例；生产中不要直接 eval 用户输入。
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"计算失败: {exc}"


# 时区工具：演示基于映射表的工具逻辑。
def city_timezone(city: str) -> str:
    """根据城市名称返回简单时区信息。"""
    mapping = {
        "北京": "UTC+8",
        "上海": "UTC+8",
        "东京": "UTC+9",
        "纽约": "UTC-5",
    }
    return mapping.get(city, "未知时区")


if __name__ == "__main__":
    # 每次运行前先检查密钥是否存在。
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    # 本示例里，模型可以在需要时调用两个工具。
    agent = create_agent(
        model="openai:gpt-4.1-mini",
        tools=[calculator, city_timezone],
        system_prompt="你是一个严谨的助手，需要优先使用工具。",
    )

    # 第一轮：让模型处理时区和计算两个子任务。
    round_1 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "东京时区是什么？另外 144/12 等于多少？",
                }
            ]
        }
    )
    print("Round1:", round_1)

    # 第二轮：独立发起另一条请求，继续观察工具路由行为。
    round_2 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "纽约时区呢？再算一下 3.14*2",
                }
            ]
        }
    )
    print("Round2:", round_2)
