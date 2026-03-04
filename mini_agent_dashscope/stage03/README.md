# Stage 03：调用 mini-agent CLI（单任务）

## 目标

- 使用 DashScope 配置后的 `mini-agent --task` 跑通一次任务

## 前提

- 已完成 Stage 01（生成 `~/.mini-agent/config/config.yaml`）
- 系统已可执行 `mini-agent` 命令

## 运行

```bash
python mini_agent_dashscope/stage03/main.py
```

自定义任务：

```bash
python mini_agent_dashscope/stage03/main.py --task "请生成 README 摘要并写入 summary.md"
```

## 验收

- 子进程成功执行
- 工作目录下出现任务产物（默认 `hello_dashscope.txt`）
