"""Stage 05: Streaming — 三种 stream_mode 对比演示。"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END


def build_graph():
    model = ChatOpenAI(model="qwen3-max")

    def draft_answer(state: MessagesState) -> dict:
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    def finalize_answer(state: MessagesState) -> dict:
        # 第二个节点：要求模型把上一步答案压缩成更精炼的版本。
        messages = state["messages"] + [
            {"role": "user", "content": "请把上面的回答整理成 3 条要点。"}
        ]
        response = model.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("draft", draft_answer)
    builder.add_node("finalize", finalize_answer)
    builder.add_edge(START, "draft")
    builder.add_edge("draft", "finalize")
    builder.add_edge("finalize", END)
    return builder.compile()


if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    graph = build_graph()
    user_input = {"messages": [{"role": "user", "content": "用三句话介绍 LangGraph。"}]}

    # --- 模式 1: values — 每步输出完整 state ---
    print("=== stream_mode='values' ===")
    for state_snapshot in graph.stream(user_input, stream_mode="values"):
        msgs = state_snapshot.get("messages", [])
        last = msgs[-1] if msgs else None
        if last:
            role = getattr(last, "type", "unknown")
            content = getattr(last, "content", "")
            if content:
                print(f"  [{role}] {content[:80]}...")
    print()

    # --- 模式 2: updates — 每步只输出增量更新 ---
    print("=== stream_mode='updates' ===")
    for update in graph.stream(user_input, stream_mode="updates"):
        for node_name, node_output in update.items():
            msgs = node_output.get("messages", [])
            if msgs:
                last = msgs[-1]
                content = getattr(last, "content", "")
                if content:
                    print(f"  [node={node_name}] {content[:80]}...")
    print()

    # --- 模式 3: messages — 逐 token 输出（打字机效果）---
    print("=== stream_mode='messages'（逐 token）===")
    current_node = None
    for chunk, metadata in graph.stream(user_input, stream_mode="messages"):
        content = getattr(chunk, "content", "")
        node_name = metadata.get("langgraph_node") if isinstance(metadata, dict) else None
        if node_name != current_node:
            current_node = node_name
            print(f"\n  [node={current_node}] ", end="", flush=True)
        if isinstance(content, str) and content:
            print(content, end="", flush=True)
    print("\n")
