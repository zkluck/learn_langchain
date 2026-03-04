# Stage 08：ACP 编辑器集成

## 目标

- 理解 ACP 适配层如何复用 Mini-Agent
- 完成编辑器侧接入验证

## 实践步骤

1. 启动 ACP 服务端

```bash
mini-agent-acp
```

2. 在支持 ACP 的客户端中配置 agent server

- 命令指向 `mini-agent-acp`
- 打开 agent 面板并创建会话

3. 验证事件流

- `newSession`
- `prompt`
- `cancel`
- tool call 状态更新

## 关键知识点

- ACP 层只是桥接，不重写核心 Agent 循环
- 每个会话都有独立 `SessionState`
- 消息更新通过 `session_notification` 回传客户端

## 验收标准

- 能在编辑器里发起一次任务并看到工具执行事件
- 能触发取消并观察停止行为

## 对应源码

- `mini_agent/acp/__init__.py`
- `mini_agent/acp/server.py`
