# Stage 05: Streaming

## 目标
- 掌握 LangGraph 图的流式输出。
- 理解 `stream_mode` 的三种模式：`values`、`updates`、`messages`。
- 能实时观察图执行过程中每个节点的输出。

## 核心概念
- **values 模式**：每个节点执行后输出完整的 state 快照。
- **updates 模式**：每个节点只输出它修改的字段（增量）。
- **messages 模式**：逐 token 输出 LLM 生成的消息内容。

## 任务
1. 运行 `main.py`，对比三种 stream_mode 的输出差异。
2. 观察多节点图中，流式输出的顺序。
3. 尝试在 messages 模式下实现打字机效果。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能解释三种 stream_mode 的区别。
- 至少用一种模式实现实时输出。
