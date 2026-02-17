"""Stage 09: Capstone — 规划 + 子代理 + 记忆 + 审批整合。"""

import os
from typing import Literal

from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command


def require_keys() -> None:
    has_model_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not has_model_key:
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("Stage 09 需要 TAVILY_API_KEY")


def resolve_model():
    model = os.getenv("DEEPAGENTS_MODEL", "openai:qwen3-max")
    if model.startswith("openai:"):
        return ChatOpenAI(model=model.split(":", 1)[1], use_responses_api=False)
    return model


def make_backend(runtime):
    return CompositeBackend(
        default=StateBackend(runtime),
        routes={"/memories/": StoreBackend(runtime)},
    )


def resume_if_interrupted(agent, result: dict, config: dict) -> dict:
    """若命中 interrupt_on，自动做审批并恢复执行。"""
    current = result
    while current.get("__interrupt__"):
        interrupts = current["__interrupt__"][0].value
        action_requests = interrupts.get("action_requests", [])

        print("=== Pending Review Actions ===")
        for action in action_requests:
            print(f"  tool={action['name']} args={action['args']}")

        # 教程示例策略：全部 approve（你可以改成按路径/工具定制）
        decisions = [{"type": "approve"} for _ in action_requests]
        current = agent.invoke(Command(resume={"decisions": decisions}), config=config)
    return current


def main() -> None:
    load_dotenv()
    require_keys()

    model = resolve_model()
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
    ):
        """联网搜索工具。"""
        return tavily_client.search(
            query,
            max_results=max_results,
            topic=topic,
            include_raw_content=include_raw_content,
        )

    research_subagent = {
        "name": "research-agent",
        "description": "处理需要更深入事实检索的问题",
        "system_prompt": "你是研究员。返回事实要点和来源摘要，保持简洁。",
        "tools": [internet_search],
    }

    agent = create_deep_agent(
        model=model,
        tools=[internet_search],
        subagents=[research_subagent],
        backend=make_backend,
        store=InMemoryStore(),
        checkpointer=MemorySaver(),
        interrupt_on={
            "write_file": {"allowed_decisions": ["approve", "reject"]},
        },
        system_prompt=(
            "你是深度研究助手。"
            "复杂问题先拆解并在必要时委派 research-agent；"
            "用户偏好写入 /memories/user_style.md；"
            "研究报告写入 /reports/*.md。"
        ),
    )

    config_user = {"configurable": {"thread_id": "capstone-user"}}
    config_task = {"configurable": {"thread_id": "capstone-task"}}

    # 1) 写入长期偏好
    turn1 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请把我的回答偏好写入 /memories/user_style.md："
                        "先给结论、使用中文、最多 6 条 bullet。"
                    ),
                }
            ]
        },
        config=config_user,
    )
    turn1 = resume_if_interrupted(agent, turn1, config_user)

    print("=== Stage 09 Turn 1 (Write Memory) ===")
    print(turn1["messages"][-1].content)

    # 2) 研究 + 写报告（可能触发 write_file 审批）
    turn2 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请研究 LangGraph 与 Deep Agents 的关系和差异，"
                        "并把结果写入 /reports/deepagents_vs_langgraph.md。"
                    ),
                }
            ]
        },
        config=config_task,
    )
    turn2 = resume_if_interrupted(agent, turn2, config_task)

    print("\n=== Stage 09 Turn 2 (Research + Write Report) ===")
    print(turn2["messages"][-1].content)

    # 3) 复读报告并应用用户偏好
    turn3 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请读取 /reports/deepagents_vs_langgraph.md，"
                        "并按我的偏好给出最终摘要。"
                    ),
                }
            ]
        },
        config=config_task,
    )

    print("\n=== Stage 09 Turn 3 (Final Summary) ===")
    print(turn3["messages"][-1].content)


if __name__ == "__main__":
    main()
