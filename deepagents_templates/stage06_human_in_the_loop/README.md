# Stage 06: Human-in-the-Loop

## 目标
- 为敏感工具配置人工审批。
- 学会处理 `__interrupt__` 并使用 `Command(resume=...)` 恢复执行。
- 实践按工具风险定制 `allowed_decisions`。

## 核心概念
- **interrupt_on**：按工具粒度启用审批。
- **Decision**：approve / edit / reject。
- **checkpointer 必需**：没有持久化无法恢复中断执行。

## 任务
1. 运行 `main.py`，观察工具调用前的中断信息。
2. 修改决策策略（比如全部 reject）并观察结果。
3. 为某个工具打开 edit 能力，手动改参数后继续。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能成功处理一次 interrupt 并恢复到最终回答。
- 能解释为什么要使用同一个 thread_id。
