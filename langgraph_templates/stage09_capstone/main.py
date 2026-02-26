"""Stage 09: 毕业项目 — 端到端工单处理图。

整合：State 设计、条件路由、本地检索、持久化、人工审批、流式输出。
"""

import operator
import sys
from datetime import datetime
from typing import Annotated
from pathlib import Path

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command


# ========== State ==========


class TicketPayload(TypedDict):
    """描述工单主体字段，确保 content/source 可被下游节点复用。"""

    content: str
    source: str


class TicketState(TypedDict):
    """Capstone 主图的标准状态结构。"""

    ticket: TicketPayload                               # 原始工单数据
    risk_flag: str                                      # 风险等级: high / low
    approved: bool                                      # 人工审批结果
    evidence: str                                       # 知识库检索到的补充信息
    priority: str                                       # P1 / P2 / P3
    result: str                                         # 最终处理结果
    logs: Annotated[list[str], operator.add]            # 执行日志（追加 reducer）


# ========== 工具函数 ==========

SENSITIVE_ACTIONS = {"删除", "清空", "停止生产", "格式化"}
RETRIEVE_HINTS = ["支付", "500", "安全", "账户", "性能", "库存", "功能", "建议", "延迟", "卡住"]


def append_log(state: TicketState, message: str) -> list[str]:
    """统一日志格式，附带时间与来源，便于串联调试记录。"""

    timestamp = datetime.now().strftime("%H:%M:%S")
    origin = state["ticket"].get("source", "unknown")
    return [f"[{timestamp}][{origin}] {message}"]


def local_retrieve(query: str) -> str:
    """从 docs/*.txt 检索命中的内容片段，并返回最多两个段落。"""

    docs_dir = Path(__file__).resolve().parent / "docs"
    hits: list[str] = []
    if not docs_dir.exists():
        return "未命中本地资料。"

    normalized_query = query.replace("，", " ").replace("。", " ")
    for fp in docs_dir.glob("*.txt"):
        text = fp.read_text(encoding="utf-8")
        for block in [segment.strip() for segment in text.split("\n\n") if segment.strip()]:
            header = block.splitlines()[0].strip()
            title = header.replace("【", "").replace("】", "")
            if title and title in normalized_query:
                hits.append(block)
                break
            if any(hint in normalized_query for hint in RETRIEVE_HINTS) and any(
                hint in block for hint in RETRIEVE_HINTS
            ):
                hits.append(block)
                break
    return "\n\n---\n\n".join(hits[:2]) if hits else "未命中本地资料。"


def build_ticket_state(content: str, source: str = "用户") -> TicketState:
    """创建具有确定初始字段的状态，模拟 receive 节点前的输入。"""

    return {
        "ticket": {"content": content, "source": source},
        "risk_flag": "low",
        "approved": False,
        "evidence": "",
        "priority": "",
        "result": "",
        "logs": [],
    }


def build_resolution(prefix: str, state: TicketState) -> str:
    """拼装处理结果，带上可用的检索证据。"""

    evidence = state.get("evidence", "")
    if evidence and evidence != "未命中本地资料。":
        return f"{prefix}\n参考信息:\n{evidence}"
    return prefix


def prompt_decision(prompt_text: str, default: str) -> str:
    """在交互环境中请求人工输入，非交互环境使用默认值。"""

    if not sys.stdin.isatty():
        print(f"  [human_review] 非交互环境，自动采用默认审批结果: {default}")
        return default
    raw = input(f"{prompt_text} (yes/no，默认 {default}): ").strip().lower()
    return raw if raw in {"yes", "no"} else default


# ========== 节点 ==========

def receive(state: TicketState) -> dict:
    """接收工单，记录来源与简要摘要。"""

    ticket = state["ticket"]
    summary = ticket["content"][:80]
    return {"logs": append_log(state, f"[receive] from {ticket['source']}: {summary}")}


def guardrail(state: TicketState) -> dict:
    """安全检查：命中敏感操作即标记为高风险。"""

    content = state["ticket"]["content"]
    for action in SENSITIVE_ACTIONS:
        if action in content:
            return {
                "risk_flag": "high",
                "logs": append_log(state, f"[guardrail] 命中敏感词: {action}"),
            }
    return {"risk_flag": "low", "logs": append_log(state, "[guardrail] 安全检查通过")}


def human_review(state: TicketState) -> dict:
    """人工审批：触发 interrupt，等待外部决定。"""

    decision = interrupt(
        f"⚠️ 高风险操作: '{state['ticket']['content']}'，是否批准？(yes/no)"
    )
    approved = str(decision).lower() == "yes"
    label = "通过" if approved else "拒绝"
    return {"approved": approved, "logs": append_log(state, f"[human_review] 审批结果: {label}")}


def retrieve(state: TicketState) -> dict:
    """本地检索补充上下文。"""

    ctx = local_retrieve(state["ticket"]["content"])
    preview = ctx if len(ctx) < 60 else f"{ctx[:57]}..."
    return {"evidence": ctx, "logs": append_log(state, f"[retrieve] {preview}")}


def classify(state: TicketState) -> dict:
    """根据关键词简单分类优先级。"""

    content = state["ticket"]["content"]
    if any(keyword in content for keyword in ["宕机", "500", "支付"]):
        priority = "P1"
    elif any(keyword in content for keyword in ["慢", "延迟", "安全", "登录", "库存"]):
        priority = "P2"
    else:
        priority = "P3"
    return {"priority": priority, "logs": append_log(state, f"[classify] 优先级: {priority}")}


def urgent_handler(state: TicketState) -> dict:
    prefix = f"🔴 P1 紧急处理: {state['ticket']['content']}"
    return {
        "result": build_resolution(prefix, state),
        "logs": append_log(state, "[urgent] 已通知值守团队"),
    }


def normal_handler(state: TicketState) -> dict:
    prefix = f"🟡 P2 普通处理: {state['ticket']['content']}"
    return {
        "result": build_resolution(prefix, state),
        "logs": append_log(state, "[normal] 已登记需求/告警"),
    }


def low_handler(state: TicketState) -> dict:
    prefix = f"🟢 P3 低优处理: {state['ticket']['content']}"
    return {
        "result": build_resolution(prefix, state),
        "logs": append_log(state, "[low] 已记录到需求池"),
    }


def reject_handler(state: TicketState) -> dict:
    prefix = f"❌ 已拒绝高危操作: {state['ticket']['content']}"
    return {
        "result": build_resolution(prefix, state),
        "logs": append_log(state, "[reject] 已拒绝并通知提单人"),
    }


# ========== 路由函数 ==========

def route_by_risk(state: TicketState) -> str:
    return "human_review" if state["risk_flag"] == "high" else "retrieve"


def route_after_review(state: TicketState) -> str:
    return "retrieve" if state.get("approved") else "reject"


def route_by_priority(state: TicketState) -> str:
    return {"P1": "urgent", "P2": "normal"}.get(state.get("priority"), "low")


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


if __name__ == "__main__":

    graph = build_graph()

    # --- 场景 1: 普通工单（低风险 → P1）---
    config1 = {"configurable": {"thread_id": "ticket-1"}}
    p1_state = build_ticket_state("支付完成后页面报 500，订单卡住", source="客服系统")
    r1 = run_with_stream_updates(graph, p1_state, config=config1)
    print_result(r1, "场景 1: 支付异常 (P1)")

    # --- 场景 2: 普通工单（低风险 → P3）---
    config2 = {"configurable": {"thread_id": "ticket-2"}}
    p3_state = build_ticket_state("希望增加深色模式功能", source="用户社区")
    r2 = graph.invoke(p3_state, config=config2)
    print_result(r2, "场景 2: 功能建议 (P3)")

    # --- 场景 3: 高危工单 → 人工审批（交互）---
    config3 = {"configurable": {"thread_id": "ticket-3"}}
    print(f"\n{'='*20} 场景 3: 高危操作 {'='*20}")
    graph.invoke(build_ticket_state("请删除用户 1024 的全部数据", source="客服系统"), config=config3)
    print("  [等待人工审批...]")
    resume_decision = prompt_decision("请输入审批结果", default="yes")
    r3 = graph.invoke(Command(resume=resume_decision), config=config3)
    print_result(r3, "场景 3: 审批结果")

    # --- 场景 4: 高危工单 → 人工审批（拒绝路径）---
    config4 = {"configurable": {"thread_id": "ticket-4"}}
    print(f"\n{'='*20} 场景 4: 高危操作（拒绝）{'='*20}")
    graph.invoke(build_ticket_state("清空生产数据库", source="上线机器人"), config=config4)
    print("  [等待人工审批...]")
    resume_decision_2 = prompt_decision("请输入审批结果", default="no")
    r4 = graph.invoke(Command(resume=resume_decision_2), config=config4)
    print_result(r4, "场景 4: 审批结果")
