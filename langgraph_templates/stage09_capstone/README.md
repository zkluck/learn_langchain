# Stage 09: 毕业项目（工单处理图）

## 目标

- 整合前 9 个阶段所学，构建完整的工单处理工作流图。
- 展示 State 设计、条件路由、工具调用、持久化、人工审批、流式输出等核心能力。

## 节点速览

- **receive**：接入外部工单，请务必保证 `content`、`source` 等字段齐全，以便后续节点引用。
- **guardrail**：根据敏感词快速决定是否走人工审批路径。
- **human_review**：使用 `interrupt()` 暂停，并等待 `Command(resume="yes/no")` 再继续。
- **retrieve**：从本地知识库 (`docs/index.txt`) 中检索相关段落，填充 `context`。
- **classify**：按照 SLA 规则把工单划分到 P1/P2/P3，随后由条件边路由到不同处理节点。
- **urgent/normal/low/reject**：终端节点，负责汇总结果、写入日志并结束流程。

## 系统架构

```
START → receive → guardrail → [条件边] → retrieve → classify → [条件边]
                                  ↓                                ↓
                           (高危 → human_review)         (P1 → urgent)
                                  ↓                       (P2 → normal)
                         (拒绝 → reject → END)            (P3 → low)
                                  ↓                             ↓
                           (通过 → retrieve)                   END
```

## 整合能力

| 能力       | 对应 Stage | 在 Capstone 中的体现                 |
| ---------- | ---------- | ------------------------------------ |
| State 设计 | Stage 01   | `TicketState`（TypedDict + Reducer） |
| 条件边路由 | Stage 02   | 按风险等级和优先级分支               |
| 工具调用   | Stage 03   | `local_retrieve` 检索本地知识库      |
| 持久化     | Stage 04   | MemorySaver + thread_id              |
| 流式输出   | Stage 05   | stream_mode="updates" 观察节点执行   |
| 人工审批   | Stage 06   | 高危操作 interrupt + resume          |
| 子图       | Stage 07   | 当前版本未内置子图，可作为扩展练习   |
| 高级模式   | Stage 08   | 条件路由与可中断流程组合             |

## 本地知识库

- `docs/index.txt` 包含常见工单类型的处理建议，由 `retrieve` 节点通过关键词匹配加载，命中文本会写入 `context` 并在日志中展示。
  - 可以根据业务场景扩充该文件，只要保持 UTF-8 文本即可被 `Path.glob("*.txt")` 捕获。
  - 若检索未命中，流程会提示“未命中本地资料”，此时仍可依靠 `classify` 继续执行。
  - 示例条目：`支付问题`（P1）、`账户安全`（P2）、`性能告警`（P1）、`库存同步`（P2）、`功能建议`（P3），均与 `docs/index.txt` 中的段落一致。

## 运行

```bash
uv run main.py
```

运行脚本后将依序演示：

1. `stream_mode="updates"` 的实时节点日志（场景一）。
2. 普通低风险工单的直接分类与处理（场景二）。
3. 高危工单触发人工审批，并在终端输入 `yes/no` 恢复流程（场景三、四）。
4. 每个场景结束后调用 `print_result`，展示优先级、结果与累计 `logs`。

## 验收标准

- 能完成端到端工单处理演示。
- 高危操作触发人工审批。
- 不同优先级走不同处理路径。
- 同一 thread 能在中断后恢复执行（状态连续）。

## 与各 Stage 的映射

- Stage 01：`TicketState` TypedDict + Reducer 聚合日志。
- Stage 02：`guardrail` / `classify` 后的条件边路由。
- Stage 03：`local_retrieve` 作为工具示例。
- Stage 04：MemorySaver+thread_id 保证恢复执行。
- Stage 05：`run_with_stream_updates` 展示 `stream_mode="updates"`。
- Stage 06：`human_review` 的 interrupt/resume。
- Stage 07：可将 urgent/normal/low 拆为子图进行扩展练习。
- Stage 08：综合路由 + 中断 + 多阶段执行策略.
