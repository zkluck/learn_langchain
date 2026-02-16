# Learn LangGraph – 分阶段实践手册

LangGraph 是 LangChain 生态中的底层图引擎，让你用"State + Node + Edge"的方式精细控制 Agent 工作流。本教程拆分为 10 个递进 Stage，帮助你从"第一个图"到"端到端工单处理系统"。

## 前置条件
- 已完成 LangChain 10 课教程（`templates/` 目录）。
- Python 3.11+，`uv` 管理依赖。
- `.env` 中配置好 `OPENAI_API_KEY`（Stage 03+ 需要）。

## Stage 总览

| Stage | 主题 | 关键能力 |
|-------|------|----------|
| 00 | Hello Graph | StateGraph / START / END / compile / invoke + **LangChain vs LangGraph 对比** |
| 01 | State 设计 | TypedDict / Pydantic State / Reducer / MessagesState |
| 02 | Nodes & Edges | add_node / add_edge / add_conditional_edges / 路由函数 |
| 03 | Tool 集成 | ChatModel.bind_tools / ToolNode / 工具循环 |
| 04 | Persistence | MemorySaver / thread_id / get_state / update_state |
| 05 | Streaming | stream_mode: values / updates / messages |
| 06 | Human-in-the-Loop | interrupt() / Command(resume=...) / 审批模式 |
| 07 | Subgraph & Multi-Agent | 子图封装 / 主图调度 / 多 Agent 协作 |
| 08 | 高级模式 | Send (map-reduce) / RetryPolicy / Command 动态路由 |
| 09 | 毕业项目 | 端到端工单处理图（整合所有能力） |

## 目录结构
```
langgraph_templates/
  stage00_hello_graph/          # Hello Graph + LangChain vs LangGraph
  stage01_state_design/         # State 设计（TypedDict / Reducer）
  stage02_nodes_edges/          # 多节点 + 条件边
  stage03_tool_integration/     # LLM + ToolNode 工具循环
  stage04_persistence/          # MemorySaver + thread_id
  stage05_streaming/            # 三种流式输出模式
  stage06_human_in_the_loop/    # interrupt + resume 审批
  stage07_subgraph_multi_agent/ # 子图 + 多 Agent
  stage08_advanced_patterns/    # Send / RetryPolicy / Command
  stage09_capstone/             # 毕业项目（工单处理图）
    docs/                       # 本地知识库
```

## 运行方式
进入对应 Stage 目录执行：
```bash
cd langgraph_templates/stage00_hello_graph
uv run main.py
```

或从仓库根目录执行：
```bash
uv run python langgraph_templates/stage00_hello_graph/main.py
```

## LangChain vs LangGraph 速查

| 场景 | 推荐 |
|------|------|
| 简单工具调用 / RAG 问答 / 结构化输出 | LangChain (`create_agent`) |
| 多步决策 / 条件分支 / 循环 | LangGraph |
| 人工审批 / 暂停恢复 | LangGraph (`interrupt`) |
| 多 Agent 协作 / 子图编排 | LangGraph |
| 精细状态控制 / 可视化流程 | LangGraph |

两者可混用：LangChain 的 `create_agent` 底层就是 LangGraph 构建的。

## 下一步
- 接入真实 LLM 做工单分类（替换 Stage 09 中的关键词匹配）。
- 用 LangSmith 追踪图执行链路。
- 将 MemorySaver 替换为持久化存储（PostgreSQL / Redis）。
- 部署到 LangGraph Agent Server。
