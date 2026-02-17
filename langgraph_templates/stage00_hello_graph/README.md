# Stage 00: Hello Graph + LangChain vs LangGraph

## 目标
- 搭建 LangGraph 运行环境。
- 理解 LangChain 与 LangGraph 的关系和适用场景。
- 跑通第一个最小 StateGraph。

## LangChain vs LangGraph：什么时候用哪个？

| 维度 | LangChain | LangGraph |
|------|-----------|-----------|
| **定位** | 高层封装，快速搭建 Agent/Chain | 底层图引擎，精细控制工作流 |
| **适合场景** | 简单工具调用、结构化输出、RAG 问答 | 多步骤决策、条件分支、循环、人工审批 |
| **控制粒度** | `create_agent` 一行搞定 | 自己定义 State → Node → Edge |
| **状态管理** | 提供 memory/checkpointer 接口，配置简单 | 同样支持 checkpointer，但你能精确控制每个节点读写哪些字段 |
| **可视化** | 黑盒，不易看到内部流转 | 天然图结构，可导出 Mermaid / 可视化 |
| **学习曲线** | 低，适合入门 | 中等，需要理解图的概念 |

**经验法则**：
- 如果 `create_agent(model, tools, system_prompt)` 就能满足需求 → 用 LangChain。
- 如果你需要**条件分支、循环、子图、人工审批、精细状态控制** → 用 LangGraph。
- 两者可以混用：LangChain 的 `create_agent` 底层就是 LangGraph 构建的。

## 任务
1. 确认 `langgraph` 已安装（`uv sync` 或 `pip install langgraph`）。
2. 运行 `main.py`，观察最小图的 invoke 结果。
3. 尝试修改节点函数，返回不同内容。

## 运行
```bash
uv run main.py
```

## 验收标准
- 终端能看到图的执行结果。
- 理解 StateGraph → add_node → add_edge → compile → invoke 的基本流程。
