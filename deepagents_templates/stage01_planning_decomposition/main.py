"""Stage 01: 规划与任务拆解 — 观察复杂任务执行。"""

import os
from collections.abc import Iterable

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI


def require_model_key() -> None:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")


def resolve_model():
    model = os.getenv("DEEPAGENTS_MODEL", "openai:qwen3-max")
    if model.startswith("openai:"):
        return ChatOpenAI(model=model.split(":", 1)[1], use_responses_api=False)
    return model


def print_stream_events(events: Iterable) -> None:
    """打印 stream_mode='updates' 的关键更新。"""
    for idx, event in enumerate(events, start=1):
        if isinstance(event, dict):
            keys = ", ".join(event.keys())
            print(f"  [{idx}] update keys: {keys}")
        else:
            print(f"  [{idx}] event: {event}")


def main() -> None:
    load_dotenv()
    require_model_key()

    model = resolve_model()
    agent = create_deep_agent(
        model=model,
        system_prompt=(
            "你是资深技术顾问。面对复杂需求时，先拆解任务，再逐步给出执行方案。"
        ),
    )

    task = (
        "请为一个 2 人团队制定‘4 周内上线 AI 工单分流 MVP’计划："
        "包含里程碑、风险、验收标准和每日执行建议。"
    )

    print("=== Stage 01 Stream Updates ===")
    events = agent.stream(
        {"messages": [{"role": "user", "content": task}]},
        stream_mode="updates",
    )
    print_stream_events(events)

    result = agent.invoke({"messages": [{"role": "user", "content": task}]})

    print("\n=== Stage 01 Final Answer ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
