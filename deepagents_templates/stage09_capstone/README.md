# Stage 09: Capstone（综合深度代理）

## 目标
- 把规划、子代理、长期记忆、人工审批组合到一个端到端流程。
- 构建“可研究、可沉淀、可审计”的最小业务助手。
- 形成可扩展的 Deep Agent 工程模板。

## 系统思路
1. 主代理接收复杂问题。
2. 必要时委派 research subagent 做深度检索。
3. 结果写入报告文件（写入前触发人工审批）。
4. 用户偏好落到 `/memories/`，支持后续会话复用。

## 整合能力
| 能力 | 对应 Stage | 在 Capstone 中的体现 |
|---|---|---|
| 规划拆解 | Stage 01 | 复杂任务自动拆解执行 |
| 上下文管理 | Stage 02 | 报告文件写入与复用 |
| 子代理 | Stage 03 | research-agent 负责深度检索 |
| Backends | Stage 04 | CompositeBackend 管理路径路由 |
| 长期记忆 | Stage 05 | `/memories/` 持久化偏好 |
| 人工审批 | Stage 06 | `interrupt_on[write_file]` |
| Skills/Memory | Stage 07 | 可继续叠加领域技能与规范 |
| 沙箱执行 | Stage 08 | 可按需接入 execute 工作流 |

## 运行
```bash
uv run main.py
```

## 验收标准
- 能处理一次“研究 + 写报告 + 审批 + 复读报告”的完整流程。
- 能在后续问题中复用 memory 偏好。
