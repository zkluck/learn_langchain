"""Stage 03: 子代理示例。"""

import os
from typing import Literal

from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI


def require_keys() -> None:
    has_model_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not has_model_key:
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")
    if not os.getenv("TAVILY_API_KEY"):
        raise RuntimeError("Stage 03 需要 TAVILY_API_KEY")


def resolve_model():
    model = os.getenv("DEEPAGENTS_MODEL", "openai:qwen3-max")
    if model.startswith("openai:"):
        return ChatOpenAI(model=model.split(":", 1)[1], use_responses_api=False)
    return model


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
        "description": "用于处理需要更深入资料检索的问题",
        "system_prompt": "你是研究员，优先收集事实并给出来源摘要。",
        "tools": [internet_search],
    }

    agent = create_deep_agent(
        model=model,
        tools=[internet_search],
        subagents=[research_subagent],
        system_prompt=(
            "你是主代理。遇到需要深度调查的问题时，优先委派 research-agent 完成子任务。"
        ),
    )

    question = (
        "请分析 LangGraph 与 Deep Agents 的关系与差异，"
        "给出 5 条要点，并补充 2 条落地建议。"
    )
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    print("=== Stage 03 Result ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
