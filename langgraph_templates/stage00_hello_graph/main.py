"""Stage 00: Hello Graph — 最小 StateGraph 示例 + LangChain vs LangGraph 对比。"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# --- 1) 定义 State：图中所有节点共享的数据结构 ---
class State(TypedDict):
    input: str
    output: str


# --- 2) 定义节点：普通 Python 函数，接收 state，返回要更新的字段 ---
def greet(state: State) -> dict:
    """最简单的节点：读取 input，写入 output。"""
    name = state["input"]
    return {"output": f"你好，{name}！欢迎来到 LangGraph。"}


# --- 3) 构建图 ---
builder = StateGraph(State)
builder.add_node("greet", greet)       # 注册节点
builder.add_edge(START, "greet")       # 入口 → greet
builder.add_edge("greet", END)         # greet → 结束

graph = builder.compile()              # 编译成可执行图


# --- 4) 运行 ---
if __name__ == "__main__":
    result = graph.invoke({"input": "LangGraph 新手"})
    print("=== Hello Graph 结果 ===")
    print(f"input:  {result['input']}")
    print(f"output: {result['output']}")

    # 再试一次，体会 invoke 的输入输出
    result2 = graph.invoke({"input": "工单系统"})
    print(f"\ninput:  {result2['input']}")
    print(f"output: {result2['output']}")
