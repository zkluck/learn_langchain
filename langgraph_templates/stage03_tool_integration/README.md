# Stage 03: Tool 集成

## 目标
- 在 LangGraph 图中接入 LLM + 工具调用。
- 学会使用 `ToolNode` 自动执行工具。
- 理解"模型调用 → 判断是否有 tool_call → 执行工具 → 回到模型"的循环。

## 核心概念
- **ToolNode**：LangGraph 内置节点，自动执行 AI 消息中的 tool_calls。
- **工具循环**：模型节点 → 条件边判断是否还有 tool_call → 有则进 ToolNode → 回到模型节点。
- **bind_tools**：把工具 schema 绑定到 ChatModel，让模型知道可以调用哪些工具。

## 任务
1. 运行 `main.py`，观察 LLM 调用工具的完整循环。
2. 添加一个新工具，观察模型如何选择。
3. 修改提问内容，触发不同工具。

## 运行
```bash
uv run main.py
```

## 验收标准
- 终端能看到模型调用工具 → 工具返回结果 → 模型生成最终回答的完整流程。
- 理解 ToolNode 和条件边在循环中的作用。
