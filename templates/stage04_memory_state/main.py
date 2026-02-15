"""Stage 04: 演示基于 thread_id 的会话记忆。"""

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from templates.common.pretty_print import pretty_print_agent_result as _pretty_print_agent_result, pretty_print_stream_event as _pretty_print_stream_event
from langgraph.checkpoint.memory import InMemorySaver


def set_preference(key: str, value: str) -> str:
    """模拟“保存用户偏好”动作。"""
    # 学习阶段先返回文本；进阶时可改成写数据库或 KV 存储。
    return f"preference_saved:{key}={value}"


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

    # InMemorySaver 会把会话状态存在内存里（程序结束后会丢失）。
    checkpointer = InMemorySaver()

    agent = create_agent(
        model="openai:qwen3-max",
        tools=[set_preference],
        system_prompt="你是会记忆上下文的助手。",
        checkpointer=checkpointer,
    )

    # thread_id 是“会话隔离键”。同一个 thread_id 会共享上下文。
    config_a = {"configurable": {"thread_id": "user-A"}}
    config_b = {"configurable": {"thread_id": "user-B"}}

    # user-A 第一轮：写入偏好。
    r1 = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "记住：我偏好中文回答。"},
            ]
        },
        config=config_a,
    )
    pretty_print_agent_result(r1, title="A-1")

    # user-A 第二轮：读取偏好，通常应能记住。
    r2 = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "我刚才偏好什么语言？"},
            ]
        },
        config=config_a,
    )
    pretty_print_agent_result(r2, title="A-2")

    # user-B 第一轮：不同 thread_id，不应继承 user-A 上下文。
    r3 = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "我刚才偏好什么语言？"},
            ]
        },
        config=config_b,
    )
    pretty_print_agent_result(r3, title="B-1")
