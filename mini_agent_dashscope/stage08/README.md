# Stage 08：MCP 配置助手（DashScope 版）

## 目标

- 生成/更新 `~/.mini-agent/config/mcp.json`
- 根据环境变量自动决定是否启用 `minimax_search`

## 运行

```bash
python mini_agent_dashscope/stage08/main.py
```

强制启用（需提供对应 key）：

```bash
python mini_agent_dashscope/stage08/main.py --enable-search --overwrite
```

## 环境变量（可选）

- `JINA_API_KEY`
- `SERPER_API_KEY`
- `MINIMAX_API_KEY`（默认回退到 `OPENAI_API_KEY`）

## 验收

- 成功生成 `mcp.json`
- 输出中明确显示搜索服务是否启用
