# Stage 00: 环境检查

验证 Python 环境和必要的环境变量是否配置正确。

## 目标

- 检查 Python 版本（需要 3.11+）
- 验证环境变量 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL`
- 打印配置信息，确保后续阶段可以正常运行

## 运行

```bash
python main.py
```

## 预期输出

```
[OK] Python 3.11.x
[OK] OPENAI_API_KEY: sk-a...9xyz
[OK] OPENAI_BASE_URL: https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
[OK] MODEL: openai:qwen3-max
环境检查通过，可以进入下一阶段
```
