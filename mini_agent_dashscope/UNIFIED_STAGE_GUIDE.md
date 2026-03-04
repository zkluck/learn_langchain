# Mini-Agent 统一阶段手册（合并版）

本文把两条线合并为一个学习路径：

- 架构/方法论文档：`mini_agent_dashscope/docs/`
- DashScope 可运行代码线：`mini_agent_dashscope/stage00~stage10`

现在统一按一套 Stage 学习，避免维护两套目录。

---

## 总览

| 统一 Stage | 目标 | 代码入口 | 理论文档（已迁移） |
|---|---|---|---|
| 00 | 环境与配置 | `mini_agent_dashscope/stage00` | `mini_agent_dashscope/docs/stage00_setup.md` |
| 01 | 生成 Mini-Agent 配置 | `mini_agent_dashscope/stage01` | `mini_agent_dashscope/docs/stage01_cli.md`（配置部分） |
| 02 | DashScope API 连通 | `mini_agent_dashscope/stage02` | `mini_agent_dashscope/docs/stage07_llm_providers.md`（协议认知） |
| 03 | mini-agent 单任务运行 | `mini_agent_dashscope/stage03` | `mini_agent_dashscope/docs/stage01_cli.md` |
| 04 | 手写工具调用循环 | `mini_agent_dashscope/stage04` | `mini_agent_dashscope/docs/stage02_agent_loop.md` + `mini_agent_dashscope/docs/stage03_tools.md` |
| 05 | 基础端到端验收 | `mini_agent_dashscope/stage05` | - |
| 06 | 记忆工具循环 | `mini_agent_dashscope/stage06` | `mini_agent_dashscope/docs/stage04_memory_logging.md` |
| 07 | 全工具循环（可选 bash） | `mini_agent_dashscope/stage07` | `mini_agent_dashscope/docs/stage03_tools.md` |
| 08 | MCP 配置助手 | `mini_agent_dashscope/stage08` | `mini_agent_dashscope/docs/stage06_mcp.md` |
| 09 | mini-agent 日志回放 | `mini_agent_dashscope/stage09` | `mini_agent_dashscope/docs/stage04_memory_logging.md` |
| 10 | 进阶总验收 | `mini_agent_dashscope/stage10` | `mini_agent_dashscope/docs/stage09_production.md`（验收思路） |

---

## 推荐顺序

1. 先跑通：`00 -> 01 -> 02 -> 03`
2. 理解核心：`04 -> 05`
3. 扩展能力：`06 -> 07 -> 08`
4. 观测与验收：`09 -> 10`

---

## 最常用命令

```bash
uv run python mini_agent_dashscope/stage05/main.py
uv run python mini_agent_dashscope/stage10/main.py
```

严格验收（包含 Stage09）：

```bash
uv run python mini_agent_dashscope/stage10/main.py --strict-mini-agent
```

---

## 维护策略

- 后续只维护 `mini_agent_dashscope/`（代码与说明同步）
- 理论文档统一放在 `mini_agent_dashscope/docs/`
- `mini_agent_stages/` 不再维护，历史文档已全部迁移到 `mini_agent_dashscope/docs/`
