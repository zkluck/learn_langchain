## Why

通过在 `langgraph_templates` 仓库中新增一个完整的毕业项目示例，可以把前八个阶段分散的知识点凝聚到一个真实业务场景里，帮助学习者验证“工单处理”类复杂流程的最佳实践，解决现有示例碎片化、缺少端到端指南的问题。

## What Changes

- 新增 README 与文档，说明毕业项目的目标、流程图以及如何运行。
- 在 `stage09_capstone` 目录下补充完整的 LangGraph 工作流，包括接收工单、守护规则、知识检索、优先级分类、人工审批、结果回写等节点。
- 整合前序阶段的关键特性（记忆、流式输出、子图、多线程、interrupt 等），提供统一的配置与演示脚本。
- 增加用于回放与测试的样例工单、日志打印工具函数，以及 `stream_mode='updates'` 观察入口。

## Capabilities

### New Capabilities
- `ticket-capstone-flow`: 毕业项目的端到端工单处理图，涵盖接收、守护、检索、分类、审批、执行、归档等节点串联。
- `ticket-stream-monitor`: 针对毕业项目提供的流式观测与日志打印工具，方便调试复杂节点间的数据流。

### Modified Capabilities
- `stage-templates-shared`: 更新公共 README 与运行指引，说明如何使用新增的毕业项目，以及与其它 stage 的衔接关系。

## Impact

- 受影响目录：`langgraph_templates/stage09_capstone/**`, `langgraph_templates/README.md`, 以及共享文档/脚本。
- 受影响依赖：LangGraph、LangChain、OpenAI/Qwen 模型调用；需要保持与现有 `.env`、MemorySaver、Command/interrupt 用法的一致性。
- 可能影响的系统：示例运行脚本与测试文档，需要验证多线程配置、持久化状态以及人工审批流程在新项目中的表现。
