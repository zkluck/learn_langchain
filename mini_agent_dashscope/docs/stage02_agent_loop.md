# Stage 02：Agent 主循环

## 目标

- 理解 `Agent.run()` 的完整执行链
- 理解终止条件、取消机制、上下文压缩机制

## 实践步骤

1. 阅读源码主流程

- `mini_agent/agent.py` 中的 `run()`

2. 重点关注分支

- LLM 返回无 `tool_calls` 时直接结束
- 有 `tool_calls` 时逐个执行工具并回填 `tool` 消息
- `max_steps` 达上限时强制停止
- `cancel_event` 生效时清理不完整消息并退出

3. 关注摘要机制

- `_summarize_messages()`
- `_create_summary()`

## 关键知识点

- Message 历史是 Agent 的“真实状态”
- token 超限后的压缩是长期任务可持续运行的关键
- 取消逻辑不只“停下来”，还要保证消息一致性

## 验收标准

- 能画出一张 `user -> llm -> tool -> llm` 回路图
- 能解释为什么要做消息清理 `_cleanup_incomplete_messages()`
- 能解释摘要后消息结构（system + user + summary）

## 对应源码

- `mini_agent/agent.py`
- `mini_agent/schema/schema.py`
