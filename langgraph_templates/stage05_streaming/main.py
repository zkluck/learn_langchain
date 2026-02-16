"""Stage 05: Streaming — 三种 stream_mode 对比演示。"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END


def build_graph():
    model = ChatOpenAI(model="qwen3-max")

    def call_model(state: MessagesState) -> dict:
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_edge(START, "model")
    builder.add_edge("model", END)
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
    print("  ", end="", flush=True)
    for chunk, metadata in graph.stream(user_input, stream_mode="messages"):
        content = getattr(chunk, "content", "")
        if isinstance(content, str) and content:
            print(content, end="", flush=True)
    print("\n")
