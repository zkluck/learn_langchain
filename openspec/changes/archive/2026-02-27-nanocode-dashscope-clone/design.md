## Context

- 目标：在 `learn_langchain/` 新建 `nanocode_dashscope/`，以 stage00–stage09 的 Python 分阶段教程展示 DashScope OpenAI 兼容接口下的 agentic loop（工具、schema、API 调用、对话循环）。
- 当前仓库虽有 LangGraph/LangChain 模板，但缺少“分阶段、零依赖 Python”对照案例，需给出逐步可运行的示例。
- 接口：`https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`，鉴权使用 `OPENAI_API_KEY`；保留 `OPENAI_BASE_URL`、`MODEL` 以便切换。
- 约束：
  1. 不引入第三方依赖，使用 Python 3.11+ 标准库（`urllib.request`、`subprocess`、`pathlib` 等）。
  2. 每个阶段独立可运行，含 README 与 main.py，便于教学。
  3. 工具、schema、循环逐步演进，最终 stage09 汇总成品。

## Goals / Non-Goals

**Goals:**

1. 提供 stage00–stage09 的 Python 示例，每阶段可运行并覆盖工具实现、schema、API 调用、对话循环。
2. 文档化 DashScope 所需环境变量（`OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL`）与常见错误，逐阶段记录。
3. 保持代码简洁、注释充分，便于与原 nanocode/ LangGraph 模板对照。

**Non-Goals:**

1. 不实现 GUI/Web，不引入 LangGraph 集成，聚焦 CLI 教程。
2. 不覆盖所有模型/地区，仅提供默认端点与可覆盖的 `MODEL`/`OPENAI_BASE_URL`。
3. 不提供复杂依赖安装，保持零第三方依赖。

## Decisions

1. **目录结构**：`nanocode_dashscope/` 下包含 stage00–stage09，每阶段 `README.md + main.py`，最终 stage09 汇总。
2. **环境变量约定**：
   - `OPENAI_API_KEY`：必需。
   - `OPENAI_BASE_URL`：默认 `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`，可覆盖。
   - `MODEL`：默认 `openai:qwen3-max`。
3. **API 客户端**：使用 Python `urllib.request` 发送 POST。
   - Headers：`Content-Type: application/json`、`Authorization: Bearer <OPENAI_API_KEY>`。
   - Body：`{ "model", "messages", "tools"?, "tool_choice"? }`，由 `json.dumps` 序列化。
   - 按阶段演进：stage05 构造 payload，stage06 实调，stage07/08 循环与 tool_calls。
4. **工具与 schema**：在前几个阶段使用 Python `pathlib`、`subprocess`、`glob` 等实现 read/write/edit/glob/grep/bash 与 schema 生成；在 stage08 支持 tool_calls。
5. **错误处理与日志**：各阶段打印 HTTP 状态/原始响应，记录常见错误；对工具执行提供错误提示（文件不存在、命令失败等）。
6. **可扩展性**：保留 env 覆盖，后续可新增工具/模型；在 README 指示如何替换 base_url。

## Risks / Trade-offs

- **DashScope function calling 兼容性** → 需验证工具 schema 能被正确消费；若暂不支持，需 fallback 为“只输出文本提示用户手动执行”。
- **超时与速率限制** → DashScope 未必与 Anthropic 相同，`bash` 工具执行 + API 请求可能叠加耗时。缓解：在 README 中记录常见报错，并在代码中设置合理超时时间（例如 60s）。
- **安全性** → `bash` 工具允许执行任意命令，与原 nanocode 一样存在风险。通过 README 明确“本地开发自用”并提示不要在敏感环境运行。

## Migration Plan

1. 创建 stage00–stage09 目录与基础 README/main.py 框架。
2. 按阶段实现：
   - stage00 环境检查
   - stage01/02/03 工具实现（IO/FS/shell，基于标准库）
   - stage04 schema 生成
   - stage05 payload 构造
   - stage06 实际调用
   - stage07 基础循环
   - stage08 带工具循环
   - stage09 汇总与示例
3. 逐阶段补充 README（运行命令、示例输出、常见错误）。
4. 完成后统一验证与补充 FAQ。

## Open Questions

1. DashScope 在 function calling 模式下返回的字段与 OpenAI 是否完全一致？需要在实现阶段通过实际请求确认。
2. 是否需要为国内/国际不同 base_url 提供自动推断（例如按环境变量 `DASHSCOPE_REGION` 切换）？暂定手动修改。
3. 是否要提供 `stream` 模式示例？初版可先不实现，如用户有需求再扩展。
