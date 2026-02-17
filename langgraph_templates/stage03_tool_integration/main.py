"""Stage 03: Tool 集成 — 在图中接入 LLM + ToolNode 实现工具调用循环。"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition


# --- 定义工具 ---

@tool
def calculator(expression: str) -> str:
    """计算数学表达式并返回结果。"""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"计算失败: {exc}"


@tool
def get_weather(city: str) -> str:
    """查询城市天气（模拟数据）。"""
    data = {"北京": "晴，25°C", "上海": "多云，22°C", "深圳": "小雨，28°C"}
    return data.get(city, f"{city}: 暂无数据")


# --- 构建图 ---

def build_graph():
    tools = [calculator, get_weather]
    tool_node = ToolNode(tools)

    # 初始化模型并绑定工具
    model = ChatOpenAI(model="qwen3-max").bind_tools(tools)

    # 模型节点：调用 LLM
    def call_model(state: MessagesState) -> dict:
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    # 构建图
    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition, {"tools": "tools", END: END})
    builder.add_edge("tools", "model")  # 工具执行完回到模型

    return builder.compile()


# --- 运行 ---

if __name__ == "__main__":
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    graph = build_graph()

    # 测试 1：触发计算工具
    print("=== 测试 1: 计算 ===")
    result = graph.invoke({"messages": [{"role": "user", "content": "计算 123 * 456 + 789"}]})
    for msg in result["messages"]:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", "")
        if content:
            print(f"  [{role}] {content}")

    # 测试 2：触发天气工具
    print("\n=== 测试 2: 天气 ===")
    result = graph.invoke({"messages": [{"role": "user", "content": "北京今天天气怎么样？"}]})
    for msg in result["messages"]:
        role = getattr(msg, "type", "unknown")
        content = getattr(msg, "content", "")
        if content:
            print(f"  [{role}] {content}")
