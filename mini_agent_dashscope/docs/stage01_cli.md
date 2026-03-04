# Stage 01：CLI 跑通

## 目标

- 掌握交互模式和单任务模式
- 熟悉会话命令与日志查看

## 实践步骤

1. 交互模式启动

```bash
mini-agent
```

2. 单任务模式启动

```bash
mini-agent --task "读取当前目录并总结项目结构"
```

3. 指定工作目录

```bash
mini-agent --workspace C:\path\to\project
```

4. 在交互态执行命令

- `/help`
- `/history`
- `/stats`
- `/log`
- `/clear`

## 关键知识点

- `--task` 会执行一次后退出
- `/log` 会打开日志目录并可直接读取日志文件
- `Esc` 可以取消当前 Agent 执行

## 验收标准

- 成功执行一次任务并输出结果
- 能查看并读懂一份 `agent_run_*.log`
- 能用 `/clear` 重置会话

## 对应源码

- `mini_agent/cli.py`
