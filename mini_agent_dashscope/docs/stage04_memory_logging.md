# Stage 04：记忆与日志

## 目标

- 理解会话记忆的实现方式
- 掌握日志追踪调试流程

## 实践步骤

1. 跑示例

```bash
uv run python examples/03_session_notes.py
```

2. 让 Agent 执行两轮任务

- 第一轮写入关键事实（例如项目偏好）
- 第二轮通过 `recall_notes` 复用事实

3. 分析日志

- 打开 `~/.mini-agent/log/`
- 选择一次 `agent_run_*.log`
- 对照 `REQUEST/RESPONSE/TOOL_RESULT` 还原问题

## 关键知识点

- 记忆文件默认路径：`workspace/.agent_memory.json`
- `record_note` / `recall_notes` 是轻量长期记忆入口
- 日志是定位“模型误判 vs 工具失败”的第一证据

## 验收标准

- `.agent_memory.json` 有可读条目
- 能用日志定位一次工具失败原因

## 对应源码

- `mini_agent/tools/note_tool.py`
- `mini_agent/logger.py`
