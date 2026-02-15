# LangChain v1 学习路径（14天，每天 1-2 小时）

## 学习目标
- 只学习 LangChain v1 主线能力（不涉及老版本迁移内容）。
- 14 天完成从最小 Agent 到可交付小项目。
- 每天都要有可运行产物（脚本、测试、或文档记录）。

## 先决条件
- Python 3.10+
- 能访问一个 LLM Provider（OpenAI 或 Anthropic）
- 使用 `uv` 管理依赖

## 项目初始化（uv）

```bash
# 1) 在项目目录创建/更新虚拟环境并安装依赖
uv sync

# 2) 配置你的模型密钥（推荐写入 .env）
cp .env.example .env
# 然后编辑 .env，把 OPENAI_API_KEY 改成你的真实 key

# 3) 运行任意阶段脚本
uv run python templates/stage00_v1_setup/main.py
```

## 常用 uv 命令

```bash
# 添加依赖
uv add 包名

# 添加开发依赖
uv add --dev 包名

# 运行脚本
uv run python 路径/脚本.py

# 运行测试
uv run pytest -q
```

## 14 天逐日计划

| Day | 时间 | 主题 | 当日产物 | 对应模板 |
|---|---:|---|---|---|
| 1 | 1-2h | v1 环境与最小 Agent | 能跑通 `create_agent` + 2个工具 | `templates/stage00_v1_setup` |
| 2 | 1-2h | Agent 主循环（单轮） | 记录一次完整“模型-工具-模型”流程 | `templates/stage01_agent_loop` |
| 3 | 1-2h | Agent 主循环（多轮） | 支持多轮问答与工具路由 | `templates/stage01_agent_loop` |
| 4 | 1-2h | Models / Messages / Tools | 3个类型化工具 + 参数校验 | `templates/stage02_models_messages_tools` |
| 5 | 1-2h | Structured Output | Pydantic schema 输出稳定通过 | `templates/stage03_structured_output_streaming` |
| 6 | 1-2h | Streaming | 终端实时打印流式事件 | `templates/stage03_structured_output_streaming` |
| 7 | 1-2h | Memory（短期） | 用同一 `thread_id` 保持会话连续 | `templates/stage04_memory_state` |
| 8 | 1-2h | State / Long-term Memory | 跨轮记住用户偏好并读取 | `templates/stage04_memory_state` |
| 9 | 1-2h | Middleware（基础） | 增加至少 1 个自定义中间件 | `templates/stage05_middleware` |
| 10 | 1-2h | Middleware（治理） | 加入重试/脱敏/限流中的 1-2 项 | `templates/stage06_reliability_safety` |
| 11 | 1-2h | RAG（2-step） | 文档检索 + 回答链路跑通 | `templates/stage07_rag_mcp` |
| 12 | 1-2h | MCP 接入 | 至少接入 1 个 MCP 资源/工具 | `templates/stage07_rag_mcp` |
| 13 | 1-2h | 测试与可观测 | 写 3 个自动化测试 + trace 记录 | `templates/stage08_testing_observability` |
| 14 | 1-2h | 毕业项目整合 | 完成可演示 Agent 小项目 | `templates/stage09_capstone` |

## 每天的统一执行动作
1. 先读当日模板目录中的 `README.md`。
2. 按 `main.py` 的 TODO 填充代码并运行。
3. 在 `notes.md`（你可自行新建）记录：问题、修复、结论。
4. 依据 README 的“验收标准”自检通过后再进入下一天。

## 阶段目录说明
- `stage00`: v1 安装与最小 Agent
- `stage01`: Agent 主循环与工具编排
- `stage02`: 模型接口、消息、工具 schema
- `stage03`: 结构化输出与流式处理
- `stage04`: 记忆与状态管理
- `stage05`: 中间件扩展
- `stage06`: 可靠性与安全治理
- `stage07`: RAG + MCP
- `stage08`: 测试与可观测
- `stage09`: 毕业项目

## 节奏建议
- 每天优先保证“跑通 + 可验证”，不要追求一次做全。
- 每两天做一次小复盘：哪些能力已稳定，哪些还不稳。
