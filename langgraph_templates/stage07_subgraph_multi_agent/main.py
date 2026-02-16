"""Stage 07: Subgraph & Multi-Agent — 子图封装 + 主图调度。"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# ========== 共享 State ==========

class MainState(TypedDict):
    query: str
    category: str
    answer: str


# ========== 子图 1: 技术支持 Agent ==========

class TechState(TypedDict):
    query: str
    answer: str


def tech_diagnose(state: TechState) -> dict:
    """技术诊断节点。"""
    return {"answer": f"[技术支持] 已排查: {state['query']}，建议检查日志和监控面板。"}


def build_tech_subgraph():
    builder = StateGraph(TechState)
    builder.add_node("diagnose", tech_diagnose)
    builder.add_edge(START, "diagnose")
    builder.add_edge("diagnose", END)
    return builder.compile()


# ========== 子图 2: 客服 Agent ==========

class ServiceState(TypedDict):
    query: str
    answer: str


def service_reply(state: ServiceState) -> dict:
    """客服回复节点。"""
    return {"answer": f"[客服] 感谢反馈: {state['query']}，我们会尽快处理。"}


def build_service_subgraph():
    builder = StateGraph(ServiceState)
    builder.add_node("reply", service_reply)
    builder.add_edge(START, "reply")
    builder.add_edge("reply", END)
    return builder.compile()


# ========== 主图 ==========

tech_graph = build_tech_subgraph()
service_graph = build_service_subgraph()


def classify_node(state: MainState) -> dict:
    """分类节点：根据关键词判断走技术还是客服。"""
    query = state["query"]
    if any(kw in query for kw in ["报错", "500", "宕机", "日志", "超时"]):
        return {"category": "tech"}
    else:
        return {"category": "service"}


def call_tech(state: MainState) -> dict:
    """调用技术支持子图。"""
    result = tech_graph.invoke({"query": state["query"]})
    return {"answer": result["answer"]}


def call_service(state: MainState) -> dict:
    """调用客服子图。"""
    result = service_graph.invoke({"query": state["query"]})
    return {"answer": result["answer"]}


def route_by_category(state: MainState) -> str:
    """路由函数。"""
    return "tech" if state["category"] == "tech" else "service"


# 构建主图
builder = StateGraph(MainState)
builder.add_node("classify", classify_node)
builder.add_node("tech", call_tech)
builder.add_node("service", call_service)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_by_category, {"tech": "tech", "service": "service"})
builder.add_edge("tech", END)
builder.add_edge("service", END)

main_graph = builder.compile()


# --- 运行 ---
if __name__ == "__main__":
    queries = [
        "接口报错 500，页面打不开",
        "想了解你们的退款政策",
        "服务器超时，请帮忙排查",
    ]

    for q in queries:
        print(f"\n查询: {q}")
        result = main_graph.invoke({"query": q, "category": "", "answer": ""})
        print(f"  分类: {result['category']}")
        print(f"  回答: {result['answer']}")
