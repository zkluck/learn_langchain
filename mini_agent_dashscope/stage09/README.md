# Stage 09：Mini-Agent 日志回放分析

## 目标

- 通过 `mini-agent --task` 执行任务
- 自动定位最新日志并输出统计摘要

## 运行

```bash
python mini_agent_dashscope/stage09/main.py
```

自定义任务：

```bash
python mini_agent_dashscope/stage09/main.py --task "创建 report.md 并写入 3 行总结"
```

## 验收

- 成功找到最新 `agent_run_*.log`
- 输出 `REQUEST/RESPONSE/TOOL_RESULT` 次数统计
