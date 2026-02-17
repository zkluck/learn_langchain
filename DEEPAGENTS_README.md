# Learn Deep Agents - 分阶段实践手册

Deep Agents 是 LangChain 生态中用于构建“深度任务代理”的 SDK，强调 **规划拆解、上下文管理、子代理委派、长期记忆、沙箱执行、人工审批**。

本教程拆分为 10 个 Stage，目标是从最小可运行示例，逐步走到“可审计、可扩展”的综合型深度代理。

## 前置条件
- Python 3.11+
- 使用 `uv` 管理依赖
- 建议已完成本仓库中的 LangChain/LangGraph 教程

## 安装依赖
在项目根目录执行：

```bash
uv sync
```

如果你只想单独补装 Deep Agents 相关依赖：

```bash
uv add deepagents==0.4.1 tavily-python
```

可选（需要沙箱执行时再安装）：

```bash
uv add langchain-daytona daytona
# 或
uv add langchain-runloop runloop-api-client
# 或
uv add langchain-modal modal
```

## 环境变量
至少配置一种模型提供方的 API Key：

```bash
OPENAI_API_KEY=your_openai_api_key
# 或
ANTHROPIC_API_KEY=your_anthropic_api_key
```

涉及联网检索的 Stage 还需要：

```bash
TAVILY_API_KEY=your_tavily_api_key
```

可选：

```bash
# 统一指定模型（默认 openai:qwen3-max）
DEEPAGENTS_MODEL=openai:qwen3-max
```

## Stage 总览

| Stage | 主题 | 关键能力 |
|---|---|---|
| 00 | Hello Deep Agent | create_deep_agent 最小可用示例 |
| 01 | 规划与任务拆解 | 复杂任务触发 write_todos（规划） |
| 02 | 上下文与虚拟文件系统 | files 注入、读写文件、线程级上下文 |
| 03 | 子代理（Subagents） | task 委派、专业子代理配置 |
| 04 | Backends 路由 | StateBackend vs FilesystemBackend |
| 05 | 长期记忆 | CompositeBackend + StoreBackend + /memories |
| 06 | Human-in-the-Loop | interrupt_on + Command(resume=...) |
| 07 | Skills + Memory 文件 | SKILL.md / AGENTS.md 组合 |
| 08 | Sandboxes + CLI | execute 工具与沙箱提供方接入 |
| 09 | Capstone | 规划 + 子代理 + 记忆 + 审批整合 |

## 目录结构

```text
deepagents_templates/
  stage00_hello_deep_agent/
  stage01_planning_decomposition/
  stage02_context_filesystem/
  stage03_subagents/
  stage04_backends/
  stage05_long_term_memory/
  stage06_human_in_the_loop/
  stage07_skills_memory/
  stage08_sandboxes_cli/
  stage09_capstone/
```

## 运行方式
进入某个阶段目录：

```bash
uv run main.py
```

或在仓库根目录运行：

```bash
uv run python deepagents_templates/stage00_hello_deep_agent/main.py
```

## 常见问题

1. `ModuleNotFoundError: deepagents`
   - 先执行：`uv add deepagents tavily-python`

2. API Key 报错
   - 检查 `.env` 是否存在，且包含对应模型提供方 Key

3. 沙箱阶段无法运行
   - 需要额外安装对应 provider 的 SDK，并配置 provider 所需环境变量

## 下一步建议
- 把 Stage 09 的示例替换为你的真实业务工具与审批策略
- 使用 LangSmith 打通 tracing 与运行审计
- 将 InMemoryStore 切换到生产级持久化存储
