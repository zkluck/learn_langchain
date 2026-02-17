# Stage 01: 规划与任务拆解

## 目标
- 体验 Deep Agent 处理复杂任务时的规划行为。
- 观察多步骤任务在流式执行中的更新事件。
- 理解内置 `write_todos` 在复杂任务中的价值。

## 核心概念
- **Planning**：代理会把大任务拆成可执行子任务。
- **write_todos**：内置任务清单能力（pending / in_progress / completed）。
- **stream**：通过流式事件观察执行轨迹。

## 任务
1. 运行 `main.py`，观察更新事件输出。
2. 修改复杂任务描述，看代理如何重新组织步骤。
3. 对比 `stream` 与 `invoke` 的体验差异。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能看到流式更新事件。
- 能解释 Deep Agent 如何处理复杂任务。
