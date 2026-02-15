# Stage 05: Middleware（基础）

## 目标
- 理解 middleware 在模型调用前后的切入点。
- 能写一个最小自定义 middleware。

## 任务
1. 在 `main.py` 里实现一个简单日志 middleware。
2. 打印每次模型调用前后的消息数量。
3. 观察 middleware 对响应的影响。

## 运行
```bash
uv run python templates/stage05_middleware/main.py
```

## 验收标准
- middleware 成功挂载并执行。
- 终端能看到前后处理日志。
