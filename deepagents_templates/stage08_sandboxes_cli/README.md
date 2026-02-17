# Stage 08: Sandboxes + CLI

## 目标
- 理解 Deep Agents 何时会启用 `execute` 工具。
- 学会按 provider 接入沙箱后端（Daytona / Runloop / Modal）。
- 熟悉 Deep Agents CLI 的基础使用方式。

## 核心概念
- **SandboxBackend**：提供隔离执行环境，代理可安全运行命令。
- **execute 工具**：只有在沙箱后端可用时才会自动注入。
- **CLI**：适合本地交互式任务和快速试验。

## 任务
1. 按 README 设置 `DEEPAGENTS_SANDBOX` 与 provider 依赖后运行。
2. 观察代理是否能执行 `python hello.py`。
3. 使用 Deep Agents CLI 完成同类任务，对比体验。

## 运行
```bash
# 任选一个 provider
export DEEPAGENTS_SANDBOX=daytona
uv run main.py
```

## CLI 快速命令
```bash
uv tool install deepagents-cli deepagents

deepagents
# 或指定模型
# deepagents --model openai:gpt-4o
```

## 验收标准
- 成功在沙箱中执行至少一个命令。
- 能解释为什么非沙箱后端没有 execute 工具。
