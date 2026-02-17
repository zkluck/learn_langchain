"""Stage 05: 长期记忆示例。"""

import os

from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore


def require_model_key() -> None:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")


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


def main() -> None:
    load_dotenv()
    require_model_key()

    model = resolve_model()
    store = InMemoryStore()
    checkpointer = MemorySaver()

    agent = create_deep_agent(
        model=model,
        backend=make_backend,
        store=store,
        checkpointer=checkpointer,
        system_prompt=(
            "你是长期记忆助手。涉及用户偏好时，请读写 /memories/ 下文件。"
        ),
    )

    config_a = {"configurable": {"thread_id": "memory-A"}}
    config_b = {"configurable": {"thread_id": "memory-B"}}

    write_turn = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请把以下信息写入 /memories/user_profile.md："
                        "用户偏好：回答简洁、先给结论、使用中文。"
                    ),
                }
            ]
        },
        config=config_a,
    )
    print("=== Stage 05 Write Memory ===")
    print(write_turn["messages"][-1].content)

    read_turn = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请读取 /memories/user_profile.md，并总结成 3 条执行规则。",
                }
            ]
        },
        config=config_b,
    )
    print("\n=== Stage 05 Read Memory (Cross Thread) ===")
    print(read_turn["messages"][-1].content)


if __name__ == "__main__":
    main()
