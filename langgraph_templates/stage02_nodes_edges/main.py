"""Stage 02: Nodes 与 Edges — 多节点图 + 条件分支。"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# --- State ---
class TicketState(TypedDict):
    content: str       # 工单内容
    priority: str      # 分类后的优先级
    route: str         # 路由目标


# --- 节点 ---
def classify(state: TicketState) -> dict:
    """根据关键词简单分类优先级。"""
    content = state["content"]
    if "宕机" in content or "500" in content:
        return {"priority": "P1", "route": "urgent"}
    elif "慢" in content or "延迟" in content:
        return {"priority": "P2", "route": "normal"}
    else:
        return {"priority": "P3", "route": "low"}


def handle_urgent(state: TicketState) -> dict:
    """处理紧急工单。"""
    print(f"  🔴 紧急处理: {state['content']}")
    return {"route": "done"}


def handle_normal(state: TicketState) -> dict:
    """处理普通工单。"""
    print(f"  🟡 普通处理: {state['content']}")
    return {"route": "done"}


def handle_low(state: TicketState) -> dict:
    """处理低优工单。"""
    print(f"  🟢 低优处理: {state['content']}")
    return {"route": "done"}


# --- 路由函数：根据 state 决定下一个节点 ---
def route_by_priority(state: TicketState) -> str:
    """条件边的路由函数，返回节点名称。"""
    mapping = {
        "urgent": "handle_urgent",
        "normal": "handle_normal",
        "low": "handle_low",
    }
    return mapping.get(state["route"], "handle_low")


# --- 构建图 ---
builder = StateGraph(TicketState)

# 注册节点
builder.add_node("classify", classify)
builder.add_node("handle_urgent", handle_urgent)
builder.add_node("handle_normal", handle_normal)
builder.add_node("handle_low", handle_low)

# 普通边：入口 → 分类
builder.add_edge(START, "classify")

# 条件边：分类后根据 route 字段决定走哪条路
builder.add_conditional_edges("classify", route_by_priority)

# 所有处理节点完成后 → 结束
builder.add_edge("handle_urgent", END)
builder.add_edge("handle_normal", END)
builder.add_edge("handle_low", END)

graph = builder.compile()


# --- 运行 ---
if __name__ == "__main__":
    tickets = [
        "服务器宕机，所有请求返回 500",
        "首页加载很慢，延迟超过 3 秒",
        "希望增加深色模式功能",
    ]

    for ticket in tickets:
        print(f"\n工单: {ticket}")
        result = graph.invoke({"content": ticket, "priority": "", "route": ""})
        print(f"  分类结果: priority={result['priority']}")
