"""Stage 09: 企业知识库问答 Capstone。"""

import os
import re
from typing import Iterable

from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command


def require_keys() -> None:
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


KNOWLEDGE_BASE: list[dict[str, str | list[str]]] = [
    {
        "id": "KB-SLA-001",
        "title": "SLA 等级与升级流程",
        "content": (
            "P1 级别：15 分钟内响应，1 小时内给出缓解方案；"
            "超过 30 分钟仍未恢复必须升级到 SRE 值班经理并同步客户。"
        ),
        "tags": ["sla", "incident", "escalation"],
    },
    {
        "id": "KB-KNOW-014",
        "title": "知识库引用规范",
        "content": (
            "客户对外邮件必须引用不少于 2 条 KB 记录，"
            "并在结尾附上后续行动与负责人。"
        ),
        "tags": ["policy", "communication"],
    },
    {
        "id": "KB-PLAYBOOK-007",
        "title": "P1 事故应急手册",
        "content": (
            "步骤：1) 建立战情群；2) 指派沟通官；3) 每 20 分钟更新客户；"
            "复盘需在 48 小时内完成并进入 CAPA。"
        ),
        "tags": ["playbook", "incident"],
    },
]


def tokenize(text: str) -> set[str]:
    return {tok for tok in re.split(r"[^\w]+", text.lower()) if tok}


def query_knowledge_base(question: str, limit: int = 3) -> list[dict[str, str]]:
    """基于内置 KB 的简易检索工具。"""
    q_tokens = tokenize(question)
    scored: list[tuple[int, dict[str, str]]] = []
    for doc in KNOWLEDGE_BASE:
        doc_text = f"{doc['title']} {doc['content']} {' '.join(doc['tags'])}"
        overlap = len(q_tokens & tokenize(doc_text))
        if overlap:
            scored.append((overlap, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    top_docs = [doc for _, doc in scored[:limit]] or KNOWLEDGE_BASE[:1]
    return [
        {
            "id": doc["id"],
            "title": doc["title"],
            "snippet": doc["content"][:200],
        }
        for doc in top_docs
    ]


def format_kb_refs(entries: Iterable[dict[str, str]]) -> str:
    return "\n".join(
        f"- {entry['id']}: {entry['title']} — {entry['snippet']}" for entry in entries
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
    kb_subagent = {
        "name": "kb-qa",
        "description": "企业知识库专家，负责命中 KB 并整理证据",
        "system_prompt": (
            "你是企业知识库分析师。"
            "遇到问题时先调用 query_knowledge_base，"
            "输出需要包含证据列表和后续行动。"
        ),
        "tools": [query_knowledge_base],
    }

    agent = create_deep_agent(
        model=model,
        tools=[query_knowledge_base],
        subagents=[kb_subagent],
        backend=make_backend,
        store=InMemoryStore(),
        checkpointer=MemorySaver(),
        interrupt_on={
            "write_file": {"allowed_decisions": ["approve", "reject"]},
        },
        system_prompt=(
            "你是企业知识库问答协调员。"
            "所有回答都需引用 query_knowledge_base 返回的记录，"
            "偏好写入 /memories/user_style.md，"
            "对外邮件草稿写入 /answers/*.md 并需审核。"
        ),
    )

    config_user = {"configurable": {"thread_id": "kbqa-user"}}
    config_task = {"configurable": {"thread_id": "kbqa-task"}}

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

    # 2) 知识库问答 + 写回答草稿（可能触发审批）
    turn2 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "客户 Cobalt Retail 提问："
                        "P1 故障期间 SLA、升级路径、以及客户通知频率是什么？"
                        "请基于企业知识库整理回复草稿，并写入 /answers/cobalt_incident.md。"
                    ),
                }
            ]
        },
        config=config_task,
    )
    turn2 = resume_if_interrupted(agent, turn2, config_task)

    print("\n=== Stage 09 Turn 2 (KB Answer Draft) ===")
    print(turn2["messages"][-1].content)

    # 3) 复读回答并引用证据
    turn3 = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请读取 /answers/cobalt_incident.md，"
                        "按我的偏好给出客户可读版本，并附上知识库引用。"
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
