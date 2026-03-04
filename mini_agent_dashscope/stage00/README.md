# Stage 00：环境检查

## 目标

- 确认 DashScope 关键环境变量是否正确
- 观察 `base_url/model` 归一化结果

## 运行

```bash
python mini_agent_dashscope/stage00/main.py
```

## 验收

- 输出中显示 `OPENAI_API_KEY` 已配置
- `base_url` 最终为 `.../chat/completions`
