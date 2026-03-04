# Stage 04：手写工具调用循环（核心）

## 目标

- 理解 function calling 的完整回路
- 在本地安全执行 `list/read/write` 三个工具

## 运行

```bash
python mini_agent_dashscope/stage04/main.py
```

自定义任务：

```bash
python mini_agent_dashscope/stage04/main.py --task "请创建 notes/todo.md，写入3条任务，再读取并总结"
```

## 验收

- 能看到 `Tool Call` 日志
- 最终输出 assistant 总结
- 工作目录中有模型创建的文件
