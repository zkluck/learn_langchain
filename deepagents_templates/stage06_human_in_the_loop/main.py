"""Stage 06: Human-in-the-Loop 示例。"""

import os
import uuid

from dotenv import load_dotenv
from langchain.tools import tool
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


@tool
def delete_file(path: str) -> str:
    """删除一个文件（示例工具，不做真实删除）。"""
    return f"[delete_file] 已删除: {path}"


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件（示例工具，不发送真实邮件）。"""
    return f"[send_email] to={to}, subject={subject}, body={body[:40]}..."


@tool
def inspect_log(path: str) -> str:
    """读取日志（示例工具，返回伪内容）。"""
    return f"[inspect_log] path={path}, content=demo-content"


def require_model_key() -> None:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")


def resolve_model():
    model = os.getenv("DEEPAGENTS_MODEL", "openai:qwen3-max")
    if model.startswith("openai:"):
        return ChatOpenAI(model=model.split(":", 1)[1], use_responses_api=False)
    return model


def resume_with_policy(agent, interrupted_result: dict, config: dict) -> dict:
    """根据工具名自动决策，然后恢复执行。"""
    current = interrupted_result
    while current.get("__interrupt__"):
        interrupts = current["__interrupt__"][0].value
        action_requests = interrupts.get("action_requests", [])

        print("=== Pending Actions ===")
        for action in action_requests:
            print(f"  tool={action['name']} args={action['args']}")

        decisions = []
        for action in action_requests:
            # 示例策略：删除动作拒绝，其它动作批准
            if action["name"] == "delete_file":
                decisions.append({"type": "reject"})
            else:
                decisions.append({"type": "approve"})

        current = agent.invoke(Command(resume={"decisions": decisions}), config=config)

    return current


def main() -> None:
    load_dotenv()
    require_model_key()

    model = resolve_model()
    checkpointer = MemorySaver()

    agent = create_deep_agent(
        model=model,
        tools=[delete_file, send_email, inspect_log],
        interrupt_on={
            "delete_file": {"allowed_decisions": ["approve", "edit", "reject"]},
            "send_email": {"allowed_decisions": ["approve", "reject"]},
            "inspect_log": False,
        },
        checkpointer=checkpointer,
        system_prompt="你是运维助手，执行敏感动作前必须等待审批。",
    )

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    prompt = "请先删除 /tmp/legacy.log，再给 admin@example.com 发邮件说明处理结果。"

    first_result = agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config,
    )

    if first_result.get("__interrupt__"):
        final_result = resume_with_policy(agent, first_result, config)
    else:
        final_result = first_result

    print("\n=== Stage 06 Final ===")
    print(final_result["messages"][-1].content)


if __name__ == "__main__":
    main()
