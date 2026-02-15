"""Stage 07: 最小 RAG 示例（本地文档检索）。"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from templates.common.pretty_print import pretty_print_agent_result as _pretty_print_agent_result, pretty_print_stream_event as _pretty_print_stream_event


def local_retrieve(query: str) -> str:
    """从 docs/*.txt 中挑选包含关键词的片段。"""
    docs_dir = Path("templates/stage07_rag_mcp/docs")
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

    # 让模型先检索，再根据检索结果回答。
    agent = create_agent(
        model="openai:qwen3-max",
        tools=[local_retrieve],
        system_prompt="回答前先检索 local_retrieve，再基于检索结果作答。",
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "根据本地资料，LangChain v1 学习重点是什么？",
                }
            ]
        }
    )
    pretty_print_agent_result(result, title="Stage 07 Result")

    # 本阶段下一步：把 MCP 资源/工具接入到同一个 Agent。
    print("TODO: 在此阶段接入 MCP 资源/工具。")
