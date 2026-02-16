# Learn LangChain – 分阶段实践手册

这个仓库将 LangChain 入门需要掌握的能力拆分成 9 个逐步递进的 Stage，帮助你在本地完成从“调用工具”到“端到端工单分流 Agent”的实践。每个 Stage 都包含 `main.py`、示例工具/模型调用和 README 任务说明，可通过 `uv run` 直接执行。

## 快速开始
1. **准备环境**
   - Python 3.11+，推荐使用 [`uv`](https://github.com/astral-sh/uv) 管理依赖。
   - 复制 `.env.example`（若存在）为 `.env`，填写 `OPENAI_API_KEY` 或兼容接口的 key。
2. **安装依赖**
   ```bash
   uv sync
   ```
3. **运行某个 Stage**（以 Stage 03 为例）：
   ```bash
   uv run python templates/stage03_structured_output_streaming/main.py
   ```
   或进入对应目录后执行 `uv run main.py`。

## Stage 总览
| Stage | 主题 | 关键能力 |
| ----- | ---- | -------- |
| 01 | Agent Loop | 观察多轮调用与工具执行流程 |
| 02 | Tools & Messages | @tool 装饰器、函数描述、工具选择 |
| 03 | Structured Output | Pydantic schema、流式输出 |
| 04 | Memory State | `thread_id` 与 `InMemorySaver` | 
| 05 | Middleware | `AgentMiddleware` 拦截模型前后逻辑 |
| 06 | Reliability & Safety | `guardrail_check` 敏感动作拦截 |
| 07 | RAG + MCP | 本地检索 `local_retrieve`、对接 MCP 资源 |
| 08 | Testing & Observability | pytest、可观测性/Tracing |
| 09 | Capstone | 集成结构化输出、RAG、记忆、守卫、测试 |

各 Stage 的 README 里提供了运行命令、任务列表与验收标准，建议按顺序完成；后续 Stage 会直接复用前一 Stage 的工具或模式。

## 目录结构
```
templates/
  stage0X_*/
    main.py            # 对应 Stage 的示例入口
    README.md          # 任务描述、运行方法
    docs/              # Stage 07/09 使用的本地知识库
templates/common/
  pretty_print.py      # 统一的终端输出工具
```

## 运行 Capstone（Stage 09）
1. 准备本地知识库 `templates/stage09_capstone/docs/*.txt`，示例已内置。
2. 在仓库根目录运行：
   ```bash
   uv run python templates/stage09_capstone/main.py
   ```
   终端会展示：
   - `guardrail_check` / `local_retrieve` / `TicketResult` 的调用轨迹；
   - `thread_id` 带来的多轮记忆；
   - 对高危请求的拦截结果。

## 测试
Stage 08 及以后推荐通过 pytest 维护回归用例，比如：
```bash
uv run pytest -q templates/stage08_testing_observability
```
你可以在各 Stage 的目录下添加更多 `test_*.py`，覆盖关键业务函数（如 `local_retrieve`、`guardrail_check`）。

## 常见问题
- **导入 `templates.*` 失败**：确保在运行脚本前将仓库根目录加入 `PYTHONPATH`，或像示例一样在文件顶部 `sys.path.append(Path(__file__).resolve().parents[2])`。
- **检索返回“未命中本地资料”**：确认 docs 目录下的文件扩展名为 `.txt`，并包含可匹配的关键词。
- **LangChain 警告 Pydantic v1**：当前依赖仍启用 Pydantic v1 兼容层，在 Python 3.14+ 会提示不兼容，但不影响示例运行。

## 下一步
- 给 Capstone 增加外部工具（如工单系统 API）。
- 引入 LangSmith / OpenTelemetry 追踪链路。
- 扩展 RAG，接入向量库或 MCP 资源。
- 将测试覆盖扩展到端到端流程。

祝你玩得开心，持续迭代自己的 LangChain Agent！
