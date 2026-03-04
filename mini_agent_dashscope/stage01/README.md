# Stage 01：生成 Mini-Agent 配置（DashScope 版）

## 目标

- 自动生成 `~/.mini-agent/config/config.yaml`
- 预置 `provider=openai` 与 DashScope 地址

## 运行

```bash
python mini_agent_dashscope/stage01/main.py
```

可选：

```bash
python mini_agent_dashscope/stage01/main.py --overwrite
```

## 验收

- `~/.mini-agent/config/config.yaml` 已生成
- `api_base` 为 DashScope 兼容地址
- `provider` 为 `openai`
