# Stage 08: 测试与可观测

## 目标
- 为核心能力写可重复执行的测试。
- 接入最小追踪（例如 LangSmith）。

## 任务
1. 运行 pytest。
2. 给测试增加至少 2 个边界场景。
3. 按你的 provider 配置追踪环境变量并观察一次链路。

## 运行
```bash
uv run pytest -q templates/stage08_testing_observability
```

## 验收标准
- 至少 3 个测试通过。
- 能通过日志或 trace 定位一次错误。
