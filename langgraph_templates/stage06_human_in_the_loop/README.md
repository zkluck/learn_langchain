# Stage 06: Human-in-the-Loop

## 目标
- 理解 LangGraph 的人工审批机制。
- 学会用 `interrupt()` 暂停图执行。
- 掌握 `Command(resume=...)` 恢复执行的模式。

## 核心概念
- **interrupt()**：在节点中调用，暂停图执行并返回一个值给调用方。
- **Command(resume=...)**：调用方审核后，用 resume 值恢复执行。
- **Checkpointer 是前提**：interrupt 依赖持久化来保存暂停时的状态。

## 典型场景
- 敏感操作前需要人工确认（如删除数据、发送邮件）。
- 模型输出需要人工校验后才能继续下一步。

## 任务
1. 运行 `main.py`，观察图在 interrupt 处暂停。
2. 模拟人工审批，用 `Command(resume=...)` 继续执行。
3. 尝试在 resume 时传入"拒绝"，观察图如何处理。

## 运行
```bash
uv run main.py
```

## 验收标准
- 图能在指定节点暂停等待人工输入。
- 人工确认后图能正确恢复并完成执行。
