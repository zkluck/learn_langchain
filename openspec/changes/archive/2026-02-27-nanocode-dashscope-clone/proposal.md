## Why

当前仓库缺少一个可逐步演示的极简代理教程，无法在本地按阶段学习 DashScope 兼容接口的 agentic loop。通过分阶段（stage00–stage09）手写 Python 版本的 nanocode，可以为 LangGraph/LangChain 学习提供细粒度对照案例，并验证国内可用模型的集成方式。

## What Changes

1. 在 `learn_langchain/` 下新建 `nanocode_dashscope` 目录，按 stage00–stage09 分阶段提供 `README.md + main.py`。
2. 逐步实现工具层、schema、API 调用、对话循环，最终在 stage09 汇总完整示例。
3. 编写针对 DashScope 的使用说明（环境变量、模型选择、错误排查），并在各阶段记录演示输出。
4. 预留扩展点（新增工具/模型切换），便于与 LangGraph/LangChain 模板对照。

## Capabilities

### New Capabilities

- `nanocode-dashscope-agent`: 分阶段的 Python 教程，演示 DashScope 兼容接口下的多轮代理（工具调用、对话历史、终端 UI）。

### Modified Capabilities

- _none_

## Impact

- 新增目录 `nanocode_dashscope/` 与 stage00–stage09 的 Python 文件/文档。
- 依赖 DashScope API（`https://dashscope.aliyuncs.com/compatible-mode/v1` 等地区端点）、环境变量 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL`。
- 需在文档中说明与现有 LangGraph 模板的关系，以及 DashScope 使用注意事项。
