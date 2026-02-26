## Context

langgraph_templates 项目此前按 Stage 展示零散示例，缺少串联各能力的端到端脚本。本设计描述如何在 stage09_capstone 中组装完整的工单处理图，涵盖守护、检索、分类、审批、执行以及流式观测。需复用 LangGraph StateGraph、MemorySaver、interrupt/Command 机制，并保持与 README、共享脚本的一致性。

## Goals / Non-Goals

**Goals:**
- 在 stage09_capstone 下提供可运行的工单处理主图，并分解为若干子节点/子图。
- 暴露日志与 stream_mode=updates 的调试入口，方便观察节点执行顺序。
- 更新共享 README，说明毕业项目如何与前序 Stage 相互呼应。

**Non-Goals:**
- 不引入新的外部依赖或模型；沿用现有 LangChain/OpenAI/Qwen 配置。
- 不实现真实工单系统后端，只提供示例流程与打印。
- 不改动已有 Stage 的代码行为，仅在 README 中说明衔接方式。

## Decisions

1. **状态结构**：采用 TypedDict 列出 `ticket`, `priority`, `result`, `logs` 等键，方便在 MemorySaver 中持久化，同时保证各节点有明确定义的输入输出字段。
2. **节点划分**：receive/guardrail/retrieve/classify/human_review/urgent/normal/low/reject 等节点使用函数组件；其中 retrieve 可模拟搜索 `docs/index.txt`，classify 根据关键词与 SLA 规则决定优先级。
3. **人工审批**：沿用 stage06 的 interrupt + Command(resume) 机制，在 human_review 节点触发暂停，仅当高危操作或策略要求人工确认时才阻断主流程。
4. **日志聚合**：通过 `append_log(state, message)` 辅助函数集中管理 `logs` 列表，避免各节点重复字符串拼接，同时便于 `ticket-stream-monitor` 能力直接消费。
5. **流式观测**：提供 `run_with_stream_updates` 辅助函数调用 `graph.stream(..., stream_mode="updates")`，实时打印节点名称，再调用 `graph.get_state` 获取最终状态。
6. **文档结构**：在 README 中新增架构图、运行示例与与 Stage 对照表，帮助学习者定位相关示例；保持 BEM/CSS 规则等全局约定。

## Risks / Trade-offs

- **风险**：流程节点过多，初学者可能难以理解 → 在 README 和日志中加入详细注释，并提供最小化示例输入。
- **风险**：人工审批依赖终端输入，CI 环境无法自动运行 → 默认示例中仅在特定触发条件下请求审批，并在文档说明如何跳过。
- **风险**：流式打印可能与主流程打印交错 → 在日志函数中加前缀、确保 flush=True，降低读写混乱。
- **风险**：新增 README 说明可能与其它 Stage 文档不一致 → 在提交前统一术语，强调这是补充说明而非替换原文。
