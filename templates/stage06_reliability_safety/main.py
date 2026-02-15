"""Stage 06: 最小安全治理示例（敏感动作拦截）。"""

import os
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from templates.common.pretty_print import pretty_print_agent_result as _pretty_print_agent_result, pretty_print_stream_event as _pretty_print_stream_event


# 可按你的业务补充敏感动作关键词。
SENSITIVE_ACTIONS = {"删除用户", "转账", "发送生产指令"}


def guardrail_check(text: str) -> str:
    """检查输入中是否包含敏感动作。"""
    for action in SENSITIVE_ACTIONS:
        if action in text:
            return f"BLOCKED: 检测到敏感动作[{action}]，需要人工确认。"
    return "PASS"


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

    # 通过系统提示约束模型“先调用 guardrail_check 再回答”。
    agent = create_agent(
        model="openai:qwen3-max",
        tools=[guardrail_check],
        system_prompt="你是安全优先的助手，先执行 guardrail_check 再回答。",
    )

    # 普通请求：应通过检查。
    normal = agent.invoke(
        {"messages": [{"role": "user", "content": "帮我写一段项目周报摘要。"}]}
    )
    pretty_print_agent_result(normal, title="Normal Request")

    # 高风险请求：应被标记为需要人工确认。
    risky = agent.invoke(
        {"messages": [{"role": "user", "content": "请直接删除用户 1024 的所有数据。"}]}
    )
    pretty_print_agent_result(risky, title="Risky Request")
