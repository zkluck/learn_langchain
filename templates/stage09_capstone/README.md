# Stage 09: 毕业项目（工单分流 Agent）

## 目标
- 整合前 8 个阶段，形成一个可演示的小系统。
- 展示结构化输出、RAG、记忆、守卫及测试等核心能力。

## 系统结构
1. **TicketResult**（Stage 03）：Pydantic schema 约束 `category/priority/reason`，确保输出稳定。
2. **local_retrieve**（Stage 07）：从 `docs/*.txt` 中检索命中文段，为回答补充上下文。
3. **guardrail_check**（Stage 06）：对输入做敏感动作拦截，命中即返回 `BLOCKED` 并提示人工确认。
4. **InMemorySaver**（Stage 04）：通过 `thread_id`（如 `user-A`）保存多轮上下文，演示记忆能力。
5. **Logging/Pretty Print**（Stage 05 & common utils）：使用公共打印工具观察消息轨迹。
6. **Tests & Observability**（Stage 08）：可依据本阶段代码编写 pytest / trace，验证关键函数与链路。

## 本地知识库（docs/）
默认提供 `docs/index.txt`，包含以下工单类型：
- 支付问题（页面 500、订单卡住）
- 账户安全（异地登录提醒、账号锁定）
- 性能告警（接口错误率、P99 超阈值）
- 库存同步（库存不准或负数）

可根据需要继续添加更多文本文件，`local_retrieve` 会自动遍历 `.txt` 文件进行关键词匹配。

## 示例流程
`main.py` 中预置了三条示例工单：
1. 支付完成后页面报 500（应分流到“支付系统”，优先级 P1）。
2. 账户异地登录被锁（命中文档，输出“账户安全”+P2）。
3. 删除用户数据（被 guardrail 拦截，分类为“安全/合规”）。

运行脚本即可在终端看到：
- 模型先后调用 `guardrail_check` / `local_retrieve` / `TicketResult` 的过程。
- 同一 `thread_id`（user-A）下的多轮对话共享上下文。
- 高危请求被拦截的结构化反馈。

## 运行
在仓库根目录执行：

```bash
uv run python templates/stage09_capstone/main.py
```

或进入本目录执行：

```bash
uv run main.py
```

## 验收标准
- 能完成端到端演示，包含结构化输出、RAG、守卫、记忆等环节。
- 出错时可通过日志或链路追踪定位问题。
- 测试覆盖关键纯函数（如 `local_retrieve`、`guardrail_check`）。
