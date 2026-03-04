# Stage 06：记忆工具循环

## 目标

- 在 DashScope function calling 循环中引入 `record_note/recall_notes`
- 让模型跨轮次复用本地记忆

## 运行

```bash
python mini_agent_dashscope/stage06/main.py
```

自定义任务：

```bash
python mini_agent_dashscope/stage06/main.py --task "记录我偏好：回答要简洁；然后回忆并总结成两条建议。"
```

## 验收

- 能看到 `record_note` 与 `recall_notes` 工具调用
- `stage06/workspace/.agent_memory.json` 写入成功
