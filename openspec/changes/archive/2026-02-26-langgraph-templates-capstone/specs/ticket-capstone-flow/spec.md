## ADDED Requirements

### Requirement: Ticket intake initializes deterministic state
系统 SHALL 通过 receive 节点接收外部工单，并初始化包含 `ticket`, `priority`, `approved`, `result`, `logs` 等字段的状态，以便后续节点和 MemorySaver 均能读取同一份上下文。

#### Scenario: Valid ticket payload
- **WHEN** 调用 `receive` 节点并传入包含 `content`、`source` 的工单数据
- **THEN** 状态 SHALL 设置 `ticket.content`、`ticket.source`，并把 `logs` 初始化为记录“工单已接收”的数组

### Requirement: Guardrail blocks high-risk content
系统 SHALL 在 guardrail 节点执行策略：若检测到 PII/高危操作（如“删除”“清空”），必须将 `risk_flag` 设为 `high` 并在未获批前阻断流程；若合规则继续进入 retrieve。

#### Scenario: High-risk instruction detected
- **WHEN** 工单描述包含“删除”或“清空”等高危关键词
- **THEN** guardrail SHALL 将 `state['risk_flag']` 设为 `high` 并写入 `logs`
- **THEN** 主图 SHALL 将流程路由至 `human_review` 节点

#### Scenario: Low-risk instruction detected
- **WHEN** 工单描述不包含任何高危关键词
- **THEN** guardrail SHALL 将 `risk_flag` 设为 `low` 并允许流程进入 `retrieve`

### Requirement: Knowledge retrieval enriches context
系统 SHALL 在 retrieve 节点读取 `docs/index.txt`（或等价检索接口），抽取与工单主题最相关的段落，将其加入 `state['evidence']`，供 classify 与执行节点引用。

#### Scenario: Docs contain matching paragraph
- **WHEN** `retrieve` 成功匹配至少一条知识库记录
- **THEN** `state['evidence']` SHALL 包含该段落文本，并记录在 `logs`

### Requirement: Priority classification drives routing
系统 SHALL 在 classify 节点依据关键词和 SLA 规则把 `priority` 设为 `P1|P2|P3`。其后应通过 `builder.add_conditional_edges` 路由到 `urgent`, `normal`, `low` 子路径，并在每条路径中生成对应的处理策略。

#### Scenario: P1 ticket routed to urgent path
- **WHEN** classify 将 `priority` 判定为 `P1`
- **THEN** 流程 SHALL 进入 `urgent` 子图，立即生成面向技术值守的回复，并在 `logs` 中标记“P1 加急”

### Requirement: Human review gates sensitive actions
系统 SHALL 在 human_review 节点对 `risk_flag == high` 的工单调用 `interrupt()`，等待人工输入 `Command(resume="yes/no")` 再决定是否继续；低风险工单不得阻塞。

#### Scenario: Reviewer approves request
- **WHEN** `risk_flag` 为 `high` 且审批人输入 `yes`
- **THEN** 节点 SHALL 将 `approved` 设为 `True`，流程返回主线继续执行

#### Scenario: Reviewer rejects request
- **WHEN** `risk_flag` 为 `high` 且审批人输入 `no`
- **THEN** 系统 SHALL 路由至 `reject` 节点，输出拒绝说明并结束流程

### Requirement: Result consolidation and persistence
系统 SHALL 在结果节点（urgent/normal/low/reject）整合 `priority`、`evidence` 与审批结果，输出结构化 `result` 文本，并通过 MemorySaver 持久化状态，允许 `graph.get_state` 随时查询。

#### Scenario: Normal priority ticket completes
- **WHEN** 工单被分类为 `P2` 且无需人工审批
- **THEN** `normal` 节点 SHALL 写入 `result`（包含行动建议与引用的 evidence）并在 `logs` 记录“流程完成”，随后 `END` 结束
