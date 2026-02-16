# Stage 08: 高级模式

## 目标
- 掌握 `Send` 实现 map-reduce 并行分发。
- 学会用 `RetryPolicy` 为节点添加重试策略。
- 理解 `Command` 同时更新状态 + 控制路由的能力。

## 核心概念
- **Send**：从条件边返回 `[Send("node", state)]` 列表，可并行分发多个任务到同一节点。
- **RetryPolicy**：为容易失败的节点（如外部 API 调用）配置自动重试次数和退避策略。
- **Command**：在节点中同时更新 state 和决定下一步走向，替代条件边。

## 任务
1. 运行 `main.py`，观察 Send 的并行分发和汇总。
2. 观察 RetryPolicy 在模拟失败时的重试行为。
3. 观察 Command 如何同时更新状态和路由。

## 运行
```bash
uv run main.py
```

## 验收标准
- 理解 Send 的 map-reduce 模式。
- RetryPolicy 能在节点失败时自动重试。
- Command 能替代条件边实现动态路由。
