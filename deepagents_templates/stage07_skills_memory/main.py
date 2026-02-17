"""Stage 07: Skills + Memory 示例。"""

import os
from pathlib import Path

from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver


def require_model_key() -> None:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")


def resolve_model():
    model = os.getenv("DEEPAGENTS_MODEL", "openai:qwen3-max")
    if model.startswith("openai:"):
        return ChatOpenAI(model=model.split(":", 1)[1], use_responses_api=False)
    return model


def main() -> None:
    load_dotenv()
    require_model_key()

    model = resolve_model()
    project_dir = Path(__file__).resolve().parent

    checkpointer = MemorySaver()
    agent = create_deep_agent(
        model=model,
        backend=FilesystemBackend(root_dir=str(project_dir), virtual_mode=True),
        skills=[str(project_dir / "skills")],
        memory=[str(project_dir / "AGENTS.md")],
        checkpointer=checkpointer,
        system_prompt="你是技术学习教练。请遵守 memory 规则，并按需调用技能。",
    )

    config = {"configurable": {"thread_id": "skills-memory-demo"}}
    prompt = "请给我一个 2 周 LangGraph 学习计划，要求每天都有可执行任务。"

    result = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config,
    )

    print("=== Stage 07 Result ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
