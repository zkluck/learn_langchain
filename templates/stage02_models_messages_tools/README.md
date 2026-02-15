# Stage 02: Models / Messages / Tools

## 目标
- 用强类型工具参数减少模型误调用。
- 明确消息结构与工具职责边界。

## 任务
1. 运行 `main.py`，理解 `@tool` 的参数定义。
2. 自增一个工具（例如汇率转换、日期计算）。
3. 对工具参数做更严格的约束（长度、范围、枚举）。

## 运行
```bash
uv run python templates/stage02_models_messages_tools/main.py
```

## 验收标准
- 至少 3 个工具，且参数带类型注解。
- 错误参数能返回可解释结果。
