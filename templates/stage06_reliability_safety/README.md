# Stage 06: 可靠性与安全

## 目标
- 在 Agent 链路中加入最小治理能力。
- 对敏感任务增加确认/拦截逻辑。

## 任务
1. 在 `main.py` 中实现敏感操作白名单。
2. 对异常响应做重试（你可在本文件中自己补充）。
3. 增加敏感词脱敏函数并接入。

## 运行
```bash
uv run python templates/stage06_reliability_safety/main.py
```

## 验收标准
- 高风险请求被拦截或要求确认。
- 普通请求可正常完成。
