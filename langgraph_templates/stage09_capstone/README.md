# Stage 09: 毕业项目（工单处理图）

## 目标
- 整合前 9 个阶段所学，构建完整的工单处理工作流图。
- 展示 State 设计、条件路由、工具调用、持久化、人工审批、流式输出等核心能力。

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
| 能力 | 对应 Stage | 在 Capstone 中的体现 |
|------|-----------|---------------------|
| State 设计 | Stage 01 | `TicketState`（TypedDict + Reducer） |
| 条件边路由 | Stage 02 | 按风险等级和优先级分支 |
| 工具调用 | Stage 03 | `local_retrieve` 检索本地知识库 |
| 持久化 | Stage 04 | MemorySaver + thread_id |
| 流式输出 | Stage 05 | stream_mode="updates" 观察节点执行 |
| 人工审批 | Stage 06 | 高危操作 interrupt + resume |
| 子图 | Stage 07 | 当前版本未内置子图，可作为扩展练习 |
| 高级模式 | Stage 08 | 条件路由与可中断流程组合 |

## 本地知识库
`docs/index.txt` 包含常见工单类型的处理建议。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能完成端到端工单处理演示。
- 高危操作触发人工审批。
- 不同优先级走不同处理路径。
- 同一 thread 能在中断后恢复执行（状态连续）。
