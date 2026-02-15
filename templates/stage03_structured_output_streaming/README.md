# Stage 03: Structured Output + Streaming

## 目标
- 让 Agent 输出稳定 JSON 结构。
- 学会流式打印中间事件。

## 任务
1. 跑通结构化输出（`response_format`）。
2. 尝试把流式事件打印出来（tokens / updates）。
3. 增加一个 schema 字段（例如 `confidence`）。

## 运行
```bash
uv run python templates/stage03_structured_output_streaming/main.py
```

## 验收标准
- 输出字段结构稳定。
- 至少打印一种流式事件。
