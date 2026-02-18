"""Stage 01: State 设计 — TypedDict / Pydantic / Reducer 对比。"""

import operator
from typing import Annotated

from pydantic import BaseModel
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState


# ========== 示例 1: 基础 TypedDict State（默认覆盖） ==========

class SimpleState(TypedDict):
    query: str
    result: str


def process_query(state: SimpleState) -> dict:
    """节点：把 query 转大写后写入 result。"""
    return {"result": state["query"].upper()}


def demo_simple_state():
    """演示：默认覆盖行为。"""
    builder = StateGraph(SimpleState)
    builder.add_node("process", process_query)
    builder.add_edge(START, "process")
    builder.add_edge("process", END)
    graph = builder.compile()

    result = graph.invoke({"query": "hello langgraph"})
    print("=== 示例 1: 基础 TypedDict State ===")
    print(f"query:  {result['query']}")
    print(f"result: {result['result']}")
    print()


# ========== 示例 1.5: Pydantic State ==========

class PydanticState(BaseModel):
    query: str
    result: str = ""


def process_with_pydantic(state: PydanticState) -> dict:
    """节点：演示 Pydantic state 也可作为图状态 schema。"""
    return {"result": f"Pydantic 处理结果: {state.query.lower()}"}


def demo_pydantic_state():
    """演示：Pydantic 作为状态 schema。"""
    builder = StateGraph(PydanticState)
    builder.add_node("process", process_with_pydantic)
    builder.add_edge(START, "process")
    builder.add_edge("process", END)
    graph = builder.compile()

    result = graph.invoke({"query": "HELLO LANGGRAPH"})
    print("=== 示例 1.5: Pydantic State ===")
    print(f"query:  {result['query']}")
    print(f"result: {result['result']}")
    print()


# ========== 示例 2: 带 Reducer 的 State（追加列表） ==========

class LogState(TypedDict):
    query: str
    # Annotated + operator.add → 每次写入都追加，而不是覆盖
    logs: Annotated[list[str], operator.add]


def step_a(state: LogState) -> dict:
    """节点 A：记录日志。"""
    return {"logs": [f"step_a 处理了: {state['query']}"]}


def step_b(state: LogState) -> dict:
    """节点 B：追加日志。"""
    return {"logs": ["step_b 完成处理"]}

def step_c(state: LogState) -> dict:
    """节点 C：追加日志。"""
    return {"logs": ["step_c 完成处理"]}


def demo_reducer_state():
    """演示：Reducer 追加列表。"""
    builder = StateGraph(LogState)
    builder.add_node("step_a", step_a)
    builder.add_node("step_b", step_b)
    builder.add_node("step_c", step_c)
    builder.add_edge(START, "step_a")
    builder.add_edge("step_a", "step_b")
    builder.add_edge("step_b", "step_c")
    builder.add_edge("step_c", END)
    graph = builder.compile()

    result = graph.invoke({"query": "测试 reducer", "logs": []})
    print("=== 示例 2: Reducer 追加列表 ===")
    print(f"query: {result['query']}")
    print(f"logs:  {result['logs']}")
    print()


# ========== 示例 3: MessagesState 快捷方式 ==========

def echo_node(state: MessagesState) -> dict:
    """节点：回显最后一条消息。"""
    last = state["messages"][-1]
    content = last.content if hasattr(last, "content") else str(last)
    return {"messages": [{"role": "ai", "content": f"收到: {content}"}]}


def demo_messages_state():
    """演示：内置 MessagesState（自带 messages + 追加 reducer）。"""
    builder = StateGraph(MessagesState)
    builder.add_node("echo", echo_node)
    builder.add_edge(START, "echo")
    builder.add_edge("echo", END)
    graph = builder.compile()

    result = graph.invoke({"messages": [{"role": "user", "content": "你好 LangGraph"}]})
    print("=== 示例 3: MessagesState ===")
    for msg in result["messages"]:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", str(msg))
        print(msg)
        print(f"  [{role}] {content}")
    print()


# ========== 入口 ==========

if __name__ == "__main__":
    demo_simple_state()
    demo_pydantic_state()
    demo_reducer_state()
    demo_messages_state()
