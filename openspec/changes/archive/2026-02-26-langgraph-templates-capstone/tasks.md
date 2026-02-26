## 1. 文档与结构

- [x] 1.1 在 `stage09_capstone` 内补充 README，加入架构图、运行指引、与前序 Stage 的映射说明。
- [x] 1.2 将 `docs/index.txt` 或同等知识库示例整理、引用到 README，标注如何被检索节点使用。

## 2. 图与状态实现

- [x] 2.1 定义 `TicketState`（TypedDict）含 `ticket/priority/approved/result/logs/evidence/risk_flag` 等字段，并集成 MemorySaver。
- [x] 2.2 实现 receive、guardrail、retrieve、classify、human_review、urgent、normal、low、reject 等节点函数，并在 builder 中串联主图与条件边。
- [x] 2.3 为 human_review 引入 interrupt / Command(resume) 分支逻辑，确保高危操作暂停且拒绝路径能写入 result。

## 3. 日志与流式监控

- [x] 3.1 编写 `append_log` 工具函数统一管理 `state['logs']`。
- [x] 3.2 实现 `run_with_stream_updates` 辅助函数：打印 `node=<name>` 序列并返回最终状态。
- [x] 3.3 更新主程序示例，展示如何使用 stream_mode="updates" 与 `graph.get_state`。

## 4. 示例与验证

- [x] 4.1 添加多条示例工单输入（含 P1/P2/P3、高危操作等）并调用主图，打印结果与日志。
- [x] 4.2 手动测试人工审批路径：确认输入 `yes/no` 可恢复执行，拒绝时走 reject。
- [x] 4.3 运行 README 中的示例命令，确保控制台输出与文档描述一致。
