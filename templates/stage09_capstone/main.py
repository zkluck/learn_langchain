"""Stage 09: 毕业项目入口模板。"""

from dotenv import load_dotenv
from langchain.agents import create_agent
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from templates.common.pretty_print import (
    pretty_print_agent_result as _pretty_print_agent_result,
    pretty_print_stream_event as _pretty_print_stream_event,
)
from pydantic import BaseModel, Field
from langgraph.checkpoint.memory import InMemorySaver
from typing import Any

# 建议你按这个顺序逐步实现：
# 1) 结构化输出（工单分类）
# 2) 本地检索（RAG）
# 3) 状态记忆（thread_id）
# 4) 安全检查（敏感动作拦截）
# 5) 测试与观测

class TicketResult(BaseModel):
    category: str = Field(description="工单分类")
    priority: str = Field(description="优先级，例如 P1/P2/P3")
    reason: str = Field(description="分类原因")


SENSITIVE_ACTIONS = {"删除用户", "清空数据库", "停止生产"}


def guardrail_check(text: str) -> str:
    """简单敏感动作拦截。如果命中关键字则返回 BLOCKED."""
    for action in SENSITIVE_ACTIONS:
        if action in text:
            return f"BLOCKED: 检测到敏感动作[{action}]，请转人工确认。"
    return "PASS"


def local_retrieve(query: str) -> str:
    """从 docs/*.txt 中挑选包含关键词的片段。"""
    # 以当前脚本所在目录为基准，避免受运行目录影响。
    docs_dir = Path(__file__).resolve().parent / "docs"
    hits: list[str] = []

    # 遍历文本文件，做最简单的关键词命中。
    if docs_dir.exists():
        for file_path in docs_dir.glob("*.txt"):
            text = file_path.read_text(encoding="utf-8")
            if any(keyword in text for keyword in query.split()):
                hits.append(f"[{file_path.name}] {text[:160]}")

    if not hits:
        return "未命中本地资料。"

    # 最多返回 3 条，避免上下文过长。
    return "\n".join(hits[:3])


def pretty_print_agent_result(result: dict[str, Any], title: str) -> None:
    _pretty_print_agent_result(result=result, title=title)


def main() -> None:
    """项目入口函数。"""
    checkpointer = InMemorySaver()

    config_a = {"configurable": {"thread_id": "user-A"}}
    config_b = {"configurable": {"thread_id": "user-risky"}}

    agent = create_agent(
        model="openai:qwen3-max",
        tools=[guardrail_check, local_retrieve],
        system_prompt=(
            "你是工单分流助手。每次回答必须先调用 guardrail_check 检查输入安全；"
            "如果通过，再调用 local_retrieve 获取补充资料，最后输出 TicketResult。"
        ),
        response_format=TicketResult,
        checkpointer=checkpointer,
    )

    payment_ticket = (
        "支付完成后页面报 500，订单状态卡住。"
    )
    security_ticket = (
        "客户账号收到异地登录提醒且被锁定。"
    )
    risky_ticket = "请立即删除用户 1024 的所有数据。"

    result_payment = agent.invoke(
        {"messages": [{"role": "user", "content": payment_ticket}]},
        config=config_a,
    )
    pretty_print_agent_result(result_payment, title="Ticket A: 支付异常")

    result_security = agent.invoke(
        {"messages": [{"role": "user", "content": security_ticket}]},
        config=config_a,
    )
    pretty_print_agent_result(result_security, title="Ticket A: 账户安全")

    result_risky = agent.invoke(
        {"messages": [{"role": "user", "content": risky_ticket}]},
        config=config_b,
    )
    pretty_print_agent_result(result_risky, title="Ticket B: 高危操作")

if __name__ == "__main__":
    load_dotenv()

    # 只有直接运行该文件时才会执行 main()。
    main()
