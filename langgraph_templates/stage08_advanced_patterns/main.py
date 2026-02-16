"""Stage 08: 高级模式 — Send (map-reduce) / RetryPolicy / Command。"""

import operator
import random
from typing import Annotated, Literal

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, Command, RetryPolicy


# =====================================================================
# 示例 1: Send — map-reduce 并行分发
# =====================================================================

class MapReduceState(TypedDict):
    topics: list[str]
    # Reducer: 每个并行节点的结果追加到 summaries
    summaries: Annotated[list[str], operator.add]


def generate_summary(state: dict) -> dict:
    """为单个 topic 生成摘要（模拟）。"""
    topic = state["topic"]
    return {"summaries": [f"[摘要] {topic}: 这是关于 {topic} 的简要总结。"]}


def fan_out_topics(state: MapReduceState) -> list[Send]:
    """条件边：为每个 topic 发送一个 Send 到 summarize 节点。"""
    return [Send("summarize", {"topic": t}) for t in state["topics"]]


def demo_send():
    """演示 Send 的 map-reduce 模式。"""
    builder = StateGraph(MapReduceState)
    builder.add_node("summarize", generate_summary)

    # START → 条件边 fan_out → 每个 topic 并行进入 summarize
    builder.add_conditional_edges(START, fan_out_topics, ["summarize"])
    builder.add_edge("summarize", END)

    graph = builder.compile()
    result = graph.invoke({"topics": ["LangGraph", "LangChain", "RAG"], "summaries": []})

    print("=== 示例 1: Send (map-reduce) ===")
    for s in result["summaries"]:
        print(f"  {s}")
    print()


# =====================================================================
# 示例 2: RetryPolicy — 自动重试
# =====================================================================

class RetryState(TypedDict):
    input: str
    output: str


attempt_counter = {"count": 0}


def flaky_node(state: RetryState) -> dict:
    """模拟不稳定的节点：前两次失败，第三次成功。"""
    attempt_counter["count"] += 1
    if attempt_counter["count"] < 3:
        raise ConnectionError(f"模拟失败 (第 {attempt_counter['count']} 次)")
    return {"output": f"成功处理: {state['input']} (第 {attempt_counter['count']} 次尝试)"}


def demo_retry():
    """演示 RetryPolicy。"""
    attempt_counter["count"] = 0

    builder = StateGraph(RetryState)
    # 为 flaky_node 配置重试策略：最多 5 次，初始延迟 0.1 秒
    builder.add_node(
        "flaky",
        flaky_node,
        retry=RetryPolicy(max_attempts=5, initial_interval=0.1),
    )
    builder.add_edge(START, "flaky")
    builder.add_edge("flaky", END)
    graph = builder.compile()

    print("=== 示例 2: RetryPolicy ===")
    try:
        result = graph.invoke({"input": "测试重试", "output": ""})
        print(f"  结果: {result['output']}")
    except Exception as e:
        print(f"  最终失败: {e}")
    print()


# =====================================================================
# 示例 3: Command — 同时更新状态 + 路由
# =====================================================================

class CommandState(TypedDict):
    value: int
    label: str
    result: str


def check_value(state: CommandState) -> Command[Literal["big_handler", "small_handler"]]:
    """用 Command 同时更新 label 并决定下一个节点。"""
    if state["value"] > 100:
        return Command(update={"label": "大数"}, goto="big_handler")
    else:
        return Command(update={"label": "小数"}, goto="small_handler")


def big_handler(state: CommandState) -> dict:
    return {"result": f"处理大数: {state['value']} (label={state['label']})"}


def small_handler(state: CommandState) -> dict:
    return {"result": f"处理小数: {state['value']} (label={state['label']})"}


def demo_command():
    """演示 Command 动态路由。"""
    builder = StateGraph(CommandState)
    builder.add_node("check", check_value)
    builder.add_node("big_handler", big_handler)
    builder.add_node("small_handler", small_handler)

    builder.add_edge(START, "check")
    builder.add_edge("big_handler", END)
    builder.add_edge("small_handler", END)
    graph = builder.compile()

    print("=== 示例 3: Command 动态路由 ===")
    for v in [50, 200]:
        result = graph.invoke({"value": v, "label": "", "result": ""})
        print(f"  value={v} → {result['result']}")
    print()


# --- 入口 ---
if __name__ == "__main__":
    demo_send()
    demo_retry()
    demo_command()
