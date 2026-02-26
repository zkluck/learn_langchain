## ADDED Requirements

### Requirement: Stream updates expose node transitions
系统 SHALL 提供 `run_with_stream_updates`（或等价接口）以 `stream_mode="updates"` 运行主图时输出节点名称序列，便于开发者理解执行拓扑。

#### Scenario: Updates stream invoked
- **WHEN** 调用 `run_with_stream_updates(graph, payload, config)`
- **THEN** 控制台 SHALL 逐行打印 `node=<name>`，并在执行完 stream 后返回 `graph.get_state(config).values`

### Requirement: Logs helper consolidates messages
系统 SHALL 暴露 `append_log(state, message)` 工具函数或同等机制，统一管理 `state['logs']` 列表，避免多节点重复拼接字符串。

#### Scenario: Node emits log entry
- **WHEN** 任意节点调用 `append_log(state, "guardrail passed")`
- **THEN** 函数 SHALL 将带时间戳或节点名称的字符串附加到 `state['logs']`

### Requirement: Stream monitor documents troubleshooting flow
项目文档 SHALL 在 README 中示例化 `stream_mode` 的使用方式，包含运行命令、示例输出以及如何借助日志来调试子图。

#### Scenario: Reader follows README guidance
- **WHEN** 用户按 README 指引执行 `python main.py` 或 `uv run main.py`
- **THEN** 文档 SHALL 解释如何切换 stream 模式、如何解读节点日志，并指明日志文件或控制台输出位置
