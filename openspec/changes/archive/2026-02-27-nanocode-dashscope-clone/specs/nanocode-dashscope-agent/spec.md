## ADDED Requirements

### Requirement: Staged Python agent must run locally without extra dependencies

系统必须提供 stage00–stage09 的 Python 示例，每个阶段可独立运行（使用 Python 3.11+ 与标准库），不依赖第三方库。

#### Scenario: 用户直接运行脚本

- **WHEN** 用户在配置好环境变量后运行任意 stage 的 `main.py`
- **THEN** 程序应成功启动并显示阶段提示/输出，不因缺少依赖报错

### Requirement: DashScope API shall be configurable via environment variables

系统必须通过 `OPENAI_API_KEY` 与可选 `OPENAI_BASE_URL`、`MODEL` 环境变量完成鉴权与模型切换，默认 base_url 为 `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`（或地区等价地址）。

#### Scenario: 默认模型运行

- **WHEN** 仅设置 `OPENAI_API_KEY`，未设置 `MODEL`
- **THEN** 系统应使用默认模型 `openai:qwen3-max` 成功调用 API 并返回响应

#### Scenario: 自定义模型运行

- **WHEN** 用户设置 `MODEL=openai:qwen3-1.8b`
- **THEN** 系统应将请求发送给 DashScope 并使用该模型生成回复

### Requirement: Tool set must include file and shell operations

代理必须在最终阶段暴露 `read`、`write`、`edit`、`glob`、`grep`、`bash` 六类工具，并通过 JSON schema 提供参数校验，允许模型在多轮推理中调用这些工具。

#### Scenario: LLM 请求读取文件

- **WHEN** DashScope 模型返回 `tool_use` 指令调用 `read`
- **THEN** 系统应执行读取、以带行号的形式返回内容，并将结果写回对话上下文供模型继续推理

#### Scenario: 执行 bash 命令

- **WHEN** 模型调用 `bash` 工具并传入命令
- **THEN** 系统应实时打印命令输出并将完整结果反馈给模型，若超时则给出超时提示

### Requirement: Conversation loop shall persist history with tool results

系统必须维护完整的对话与工具结果（stage07 基础循环、stage08 工具循环），确保 DashScope 模型可以多次请求工具并基于最新上下文继续生成，直到模型返回纯文本结束本轮交互。

#### Scenario: 多次工具调用

- **WHEN** 模型在一次用户提问中连续调用多个工具
- **THEN** 系统必须依次执行，记录每次结果，并在模型返回最终文本后再结束循环

### Requirement: CLI UX shall provide clear feedback with separators and colors

终端交互需包含醒目的提示符、分隔线、工具调用摘要与错误提示颜色，以便用户观察代理行为。

#### Scenario: 工具调用输出

- **WHEN** 任何工具被调用
- **THEN** 终端应打印工具名称、参数预览及结果摘要，并使用 ANSI 颜色区分文本、工具、错误信息
