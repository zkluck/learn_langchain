"""Stage 01: 观察 Agent 在多轮请求中的工具调用循环。"""

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from templates.common.pretty_print import pretty_print_agent_result as _pretty_print_agent_result, pretty_print_stream_event as _pretty_print_stream_event


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


def pretty_print_agent_result(result: dict[str, Any], title: str = "Agent 执行结果") -> None:
    """调用公共打印工具，展示消息核心返回值。"""
    _pretty_print_agent_result(result=result, title=title)


def pretty_print_stream_event(event: Any) -> None:
    """调用公共打印工具，展示流式事件核心信息。"""
    _pretty_print_stream_event(event)

if __name__ == "__main__":
    # 自动读取项目根目录下的 .env 文件（如果存在）。
    load_dotenv()

    # 每次运行前先检查密钥是否存在。
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    # 本示例里，模型可以在需要时调用两个工具。
    agent = create_agent(
        model="openai:qwen3-max",
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
    pretty_print_agent_result(round_1, title="Round 1")

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
    pretty_print_agent_result(round_2, title="Round 2")
