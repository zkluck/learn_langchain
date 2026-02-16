# Stage 04: Persistence & Checkpointing

## 目标
- 理解 LangGraph 的持久化机制：Checkpointer + Thread。
- 学会用 `MemorySaver` 实现多轮对话记忆。
- 掌握 `get_state` / `update_state` 查看和修改图状态。

## 核心概念
- **Checkpointer**：在每个节点执行后自动保存状态快照，支持恢复和回放。
- **Thread**：通过 `thread_id` 隔离不同会话，同一 thread 共享历史。
- **get_state**：查看某个 thread 当前的完整状态。
- **update_state**：手动修改某个 thread 的状态（调试或纠偏时有用）。

## 任务
1. 运行 `main.py`，观察同一 thread 内多轮对话的上下文保持。
2. 用 `get_state` 查看保存的状态内容。
3. 切换 `thread_id`，验证不同会话互不影响。

## 运行
```bash
uv run main.py
```

## 验收标准
- 同一 thread 的第二轮对话能记住第一轮内容。
- 不同 thread 之间状态隔离。
