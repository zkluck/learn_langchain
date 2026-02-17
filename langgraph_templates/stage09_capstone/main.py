"""Stage 09: 毕业项目 — 端到端工单处理图。

整合：State 设计、条件路由、本地检索、持久化、人工审批、流式输出。
"""

import operator
from typing import Annotated
from pathlib import Path

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command


# ========== State ==========

class TicketState(TypedDict):
    content: str                                        # 原始工单内容
    risk: str                                           # 风险等级: high / low
    approved: bool                                      # 人工审批结果
    context: str                                        # RAG 检索到的补充信息
    priority: str                                       # P1 / P2 / P3
    result: str                                         # 最终处理结果
    logs: Annotated[list[str], operator.add]             # 执行日志（追加 reducer）


# ========== 工具函数 ==========

SENSITIVE_ACTIONS = {"删除", "清空", "停止生产", "格式化"}


def local_retrieve(query: str) -> str:
    """从 docs/*.txt 检索命中的内容片段。"""
    docs_dir = Path(__file__).resolve().parent / "docs"
    hits: list[str] = []
    if docs_dir.exists():
        for fp in docs_dir.glob("*.txt"):
            text = fp.read_text(encoding="utf-8")
            if any(kw in text for kw in query.split()):
                hits.append(text[:200])
    return "\n".join(hits[:3]) if hits else "未命中本地资料。"


# ========== 节点 ==========

def receive(state: TicketState) -> dict:
    """接收工单。"""
    return {"logs": [f"[receive] 收到工单: {state['content']}"]}


def guardrail(state: TicketState) -> dict:
    """安全检查：判断是否包含敏感动作。"""
    content = state["content"]
    for action in SENSITIVE_ACTIONS:
        if action in content:
            return {"risk": "high", "logs": [f"[guardrail] 命中敏感词: {action}"]}
    return {"risk": "low", "logs": ["[guardrail] 安全检查通过"]}


def human_review(state: TicketState) -> dict:
    """人工审批：高风险时 interrupt 等待确认。"""
    decision = interrupt(f"⚠️ 高风险操作: '{state['content']}'，是否批准？(yes/no)")
    approved = str(decision).lower() == "yes"
    label = "通过" if approved else "拒绝"
    return {"approved": approved, "logs": [f"[human_review] 审批结果: {label}"]}


def retrieve(state: TicketState) -> dict:
    """本地检索补充上下文。"""
    ctx = local_retrieve(state["content"])
    return {"context": ctx, "logs": [f"[retrieve] 检索结果: {ctx[:60]}..."]}


def classify(state: TicketState) -> dict:
    """根据关键词简单分类优先级。"""
    content = state["content"]
    if "宕机" in content or "500" in content or "支付" in content:
        p = "P1"
    elif "慢" in content or "延迟" in content or "安全" in content or "登录" in content:
        p = "P2"
    else:
        p = "P3"
    return {"priority": p, "logs": [f"[classify] 优先级: {p}"]}


def urgent_handler(state: TicketState) -> dict:
    return {"result": f"🔴 P1 紧急处理: {state['content']}", "logs": ["[urgent] 已处理"]}


def normal_handler(state: TicketState) -> dict:
    return {"result": f"🟡 P2 普通处理: {state['content']}", "logs": ["[normal] 已处理"]}


def low_handler(state: TicketState) -> dict:
    return {"result": f"🟢 P3 低优处理: {state['content']}", "logs": ["[low] 已处理"]}


def reject_handler(state: TicketState) -> dict:
    return {"result": f"❌ 已拒绝高危操作: {state['content']}", "logs": ["[reject] 已拒绝"]}


# ========== 路由函数 ==========

def route_by_risk(state: TicketState) -> str:
    return "human_review" if state["risk"] == "high" else "retrieve"


def route_after_review(state: TicketState) -> str:
    return "retrieve" if state["approved"] else "reject"


def route_by_priority(state: TicketState) -> str:
    return {"P1": "urgent", "P2": "normal"}.get(state["priority"], "low")


# ========== 构建图 ==========

def build_graph():
    builder = StateGraph(TicketState)

    # 注册节点
    builder.add_node("receive", receive)
    builder.add_node("guardrail", guardrail)
    builder.add_node("human_review", human_review)
    builder.add_node("retrieve", retrieve)
    builder.add_node("classify", classify)
    builder.add_node("urgent", urgent_handler)
    builder.add_node("normal", normal_handler)
    builder.add_node("low", low_handler)
    builder.add_node("reject", reject_handler)

    # 边
    builder.add_edge(START, "receive")
    builder.add_edge("receive", "guardrail")

    # 安全检查后：高风险 → 人工审批，低风险 → 检索
    builder.add_conditional_edges("guardrail", route_by_risk,
                                  {"human_review": "human_review", "retrieve": "retrieve"})

    # 审批后：通过 → 检索，拒绝 → reject
    builder.add_conditional_edges("human_review", route_after_review,
                                  {"retrieve": "retrieve", "reject": "reject"})

    builder.add_edge("retrieve", "classify")

    # 分类后：按优先级路由
    builder.add_conditional_edges("classify", route_by_priority,
                                  {"urgent": "urgent", "normal": "normal", "low": "low"})

    # 所有终端节点 → END
    for node in ["urgent", "normal", "low", "reject"]:
        builder.add_edge(node, END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


# ========== 辅助打印 ==========

def print_result(result: dict, title: str):
    print(f"\n{'='*20} {title} {'='*20}")
    print(f"  优先级: {result.get('priority', '-')}")
    print(f"  结果:   {result.get('result', '-')}")
    print(f"  日志:")
    for log in result.get("logs", []):
        print(f"    {log}")


def run_with_stream_updates(graph, payload: dict, config: dict) -> dict:
    """用 updates 模式执行一次，并返回最终状态。"""
    print("  [stream_mode='updates']")
    for update in graph.stream(payload, config=config, stream_mode="updates"):
        for node_name in update.keys():
            print(f"    -> node={node_name}")

    # stream(mode=updates) 返回增量，最终完整状态可从 checkpointer 读取
    snapshot = graph.get_state(config)
    return snapshot.values


# ========== 入口 ==========

EMPTY = {"content": "", "risk": "", "approved": False, "context": "",
         "priority": "", "result": "", "logs": []}


if __name__ == "__main__":

    graph = build_graph()

    # --- 场景 1: 普通工单（低风险 → P1）---
    config1 = {"configurable": {"thread_id": "ticket-1"}}
    r1 = run_with_stream_updates(
        graph,
        {**EMPTY, "content": "支付完成后页面报 500，订单卡住"},
        config=config1,
    )
    print_result(r1, "场景 1: 支付异常 (P1)")

    # --- 场景 2: 普通工单（低风险 → P3）---
    config2 = {"configurable": {"thread_id": "ticket-2"}}
    r2 = graph.invoke({**EMPTY, "content": "希望增加深色模式功能"}, config=config2)
    print_result(r2, "场景 2: 功能建议 (P3)")

    # --- 场景 3: 高危工单 → 人工审批 → 批准 ---
    config3 = {"configurable": {"thread_id": "ticket-3"}}
    print(f"\n{'='*20} 场景 3: 高危操作 {'='*20}")
    graph.invoke({**EMPTY, "content": "请删除用户 1024 的全部数据"}, config=config3)
    print("  [等待人工审批...]")

    r3 = graph.invoke(Command(resume="yes"), config=config3)
    print_result(r3, "场景 3: 审批通过后")

    # --- 场景 4: 高危工单 → 人工审批 → 拒绝 ---
    config4 = {"configurable": {"thread_id": "ticket-4"}}
    print(f"\n{'='*20} 场景 4: 高危操作（拒绝）{'='*20}")
    graph.invoke({**EMPTY, "content": "清空生产数据库"}, config=config4)
    print("  [等待人工审批...]")

    r4 = graph.invoke(Command(resume="no"), config=config4)
    print_result(r4, "场景 4: 审批拒绝")
