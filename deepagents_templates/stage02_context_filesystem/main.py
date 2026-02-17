"""Stage 02: 上下文与虚拟文件系统。"""

import os

from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
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
    checkpointer = MemorySaver()

    agent = create_deep_agent(
        model=model,
        checkpointer=checkpointer,
        system_prompt=(
            "你是项目执行助手。面对复杂需求时，优先读写文件来管理上下文，"
            "并给出结构化输出。"
        ),
    )

    config = {"configurable": {"thread_id": "ctx-demo-thread"}}

    seed_files = {
        "/notes/requirements.txt": create_file_data(
            "项目目标：2 周内交付工单分流 MVP。\n"
            "约束：后端 1 人、前端 1 人；不能新增外部中间件。\n"
            "重点：高优工单优先、保留人工审批入口。"
        )
    }

    first_turn = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请先读取 /notes/requirements.txt，然后写一个 6 条待办清单到 "
                        "/notes/todo.md，最后简述关键风险。"
                    ),
                }
            ],
            "files": seed_files,
        },
        config=config,
    )

    print("=== Stage 02 First Turn ===")
    print(first_turn["messages"][-1].content)

    second_turn = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请读取 /notes/todo.md，并原样返回文件内容。",
                }
            ]
        },
        config=config,
    )

    print("\n=== Stage 02 Second Turn ===")
    print(second_turn["messages"][-1].content)


if __name__ == "__main__":
    main()
