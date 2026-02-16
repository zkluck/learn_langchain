"""Stage 04: Persistence — MemorySaver + thread_id 实现多轮记忆。"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver


def build_graph():
    model = ChatOpenAI(model="qwen3-max")

    def call_model(state: MessagesState) -> dict:
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_edge(START, "model")
    builder.add_edge("model", END)

    # 编译时传入 checkpointer，启用持久化
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    graph = build_graph()

    # --- Thread A: 多轮对话 ---
    config_a = {"configurable": {"thread_id": "thread-A"}}

    print("=== Thread A: 第 1 轮 ===")
    r1 = graph.invoke(
        {"messages": [{"role": "user", "content": "记住：我的名字是小明。"}]},
        config=config_a,
    )
    last_msg = r1["messages"][-1]
    print(f"  AI: {last_msg.content}")

    print("\n=== Thread A: 第 2 轮 ===")
    r2 = graph.invoke(
        {"messages": [{"role": "user", "content": "我叫什么名字？"}]},
        config=config_a,
    )
    last_msg = r2["messages"][-1]
    print(f"  AI: {last_msg.content}")

    # --- Thread B: 新会话，不共享记忆 ---
    config_b = {"configurable": {"thread_id": "thread-B"}}

    print("\n=== Thread B: 新会话 ===")
    r3 = graph.invoke(
        {"messages": [{"role": "user", "content": "我叫什么名字？"}]},
        config=config_b,
    )
    last_msg = r3["messages"][-1]
    print(f"  AI: {last_msg.content}")

    # --- 查看状态 ---
    print("\n=== get_state: Thread A 的状态 ===")
    state_a = graph.get_state(config_a)
    print(f"  消息数量: {len(state_a.values['messages'])}")
    for i, msg in enumerate(state_a.values["messages"]):
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", "")[:60]
        print(f"  {i+1}. [{role}] {content}")
