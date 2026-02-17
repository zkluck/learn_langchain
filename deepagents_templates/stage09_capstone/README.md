# Stage 09: 企业知识库问答 Capstone

## 目标
- 构建一个企业内部知识库问答（Enterprise KB QA）工作流，整合规划、子代理、记忆与审批。
- 演示“知识洞察 → 合规审阅 → 输出归档”这一真实业务闭环。
- 给出可复用的 Deep Agent 模板，便于接入自家 KB、权限与审计体系。

## 架构与职责
| 模块 | 职责 | 对应能力 |
| --- | --- | --- |
| 主代理（KB Orchestrator） | 协调复杂问答、选择是否调用子代理/工具、触发写入流程 | Stage 01, Stage 02 |
| `kb-qa` 子代理 | 负责命中知识库、整理证据并返回结构化摘要 | Stage 03 |
| CompositeBackend | 将 `/memories/` 写入持久化区域、`/answers/` 走文件系统路由，方便审计 | Stage 04 |
| Long-term Memory | `/memories/user_style.md` 持久化回答偏好，后续所有问答可复用 | Stage 05 |
| 审批节点 | `interrupt_on["write_file"]`，在对外发布前要求人工批准 | Stage 06 |
| Skills / Memory | 可叠加企业规范、术语表，提高回答一致性 | Stage 07 |
| Sandbox（可选） | 若要在沙箱中执行验证脚本，可复用 Stage 08 的方法 | Stage 08 |

## 运行步骤
1. 准备环境变量（至少 `OPENAI_API_KEY` **或** `ANTHROPIC_API_KEY`）。
2. 运行示例：
   ```bash
   uv run main.py
   ```
3. 观察三个阶段的输出：
   - 偏好落库：把用户回答偏好写入 `/memories/user_style.md`。
   - KB 问答：围绕企业知识库数据回答问题。
   - 合规审批：生成对外回复草稿，并写入 `/answers/*.md`，需要审批后才算完成。

## 验收标准
- 至少展示一次“记忆偏好 → KB 检索 → 审批写入 → 复读结果”的闭环。
- 终端打印需包括：待审批动作、批准后的最终回答、以及从知识库抽取的信息片段。
- 允许将本地知识库替换成企业真实 KB，只需保持工具签名一致。
