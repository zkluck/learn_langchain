"""Stage 06: Human-in-the-Loop — interrupt / Command(resume) 审批模式。"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command


# --- State ---
class ApprovalState(TypedDict):
    request: str       # 用户请求
    risk_level: str    # 风险等级
    approved: bool     # 是否通过审批
    result: str        # 最终结果


# --- 节点 ---
def analyze_risk(state: ApprovalState) -> dict:
    """分析请求的风险等级。"""
    request = state["request"]
    if "删除" in request or "清空" in request:
        level = "high"
    elif "修改" in request:
        level = "medium"
    else:
        level = "low"
    print(f"  [analyze] 风险等级: {level}")
    return {"risk_level": level}


def human_review(state: ApprovalState) -> dict:
    """人工审批节点：高风险时暂停等待确认。"""
    if state["risk_level"] == "high":
        # interrupt() 会暂停图执行，返回提示给调用方
        decision = interrupt(
            f"⚠️ 高风险操作: '{state['request']}'，是否批准？(yes/no)"
        )
        approved = decision.lower() == "yes"
        print(f"  [human_review] 审批结果: {'通过' if approved else '拒绝'}")
        return {"approved": approved}
    else:
        print(f"  [human_review] 低/中风险，自动通过")
        return {"approved": True}


def execute_action(state: ApprovalState) -> dict:
    """执行操作或拒绝。"""
    if state["approved"]:
        return {"result": f"✅ 已执行: {state['request']}"}
    else:
        return {"result": f"❌ 已拒绝: {state['request']}"}


# --- 构建图 ---
builder = StateGraph(ApprovalState)
builder.add_node("analyze", analyze_risk)
builder.add_node("review", human_review)
builder.add_node("execute", execute_action)

builder.add_edge(START, "analyze")
builder.add_edge("analyze", "review")
builder.add_edge("review", "execute")
builder.add_edge("execute", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# --- 运行 ---
if __name__ == "__main__":

    # === 场景 1: 低风险操作 — 自动通过 ===
    print("=== 场景 1: 低风险 ===")
    config1 = {"configurable": {"thread_id": "req-1"}}
    r1 = graph.invoke(
        {"request": "查询用户信息", "risk_level": "", "approved": False, "result": ""},
        config=config1,
    )
    print(f"  结果: {r1['result']}\n")

    # === 场景 2: 高风险操作 — 需要人工审批 ===
    print("=== 场景 2: 高风险（第一步：触发 interrupt）===")
    config2 = {"configurable": {"thread_id": "req-2"}}
    r2 = graph.invoke(
        {"request": "删除用户 1024 的全部数据", "risk_level": "", "approved": False, "result": ""},
        config=config2,
    )
    # 此时图暂停在 review 节点，r2 包含 interrupt 的提示信息
    print(f"  图暂停，等待审批...")

    # 模拟人工批准
    print("\n=== 场景 2: 人工批准，恢复执行 ===")
    r2_resumed = graph.invoke(Command(resume="yes"), config=config2)
    print(f"  结果: {r2_resumed['result']}\n")

    # === 场景 3: 高风险操作 — 人工拒绝 ===
    print("=== 场景 3: 高风险（人工拒绝）===")
    config3 = {"configurable": {"thread_id": "req-3"}}
    graph.invoke(
        {"request": "清空生产数据库", "risk_level": "", "approved": False, "result": ""},
        config=config3,
    )
    print(f"  图暂停，等待审批...")

    r3_resumed = graph.invoke(Command(resume="no"), config=config3)
    print(f"  结果: {r3_resumed['result']}")
