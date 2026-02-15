# Stage 01: Agent 主循环

## 目标
- 理解单轮/多轮里，模型与工具的循环。
- 学会为 Agent 准备多轮 `messages`。

## 任务
1. 运行 `main.py`，观察两轮输入的结果。
2. 为工具增加异常处理（例如除零）。
3. 在终端记录每轮请求的输入与输出。

## 运行
```bash
uv run python templates/stage01_agent_loop/main.py
```

## 验收标准
- 同一脚本中完成至少两轮请求。
- 至少一个工具分支正确触发。
