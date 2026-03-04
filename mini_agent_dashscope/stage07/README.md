# Stage 07：全工具循环（含可选 Bash）

## 目标

- 扩展到 `list/read/write/edit/glob/grep/bash` 全工具
- 在 DashScope 下体验更接近真实工程场景的工具编排

## 运行

```bash
python mini_agent_dashscope/stage07/main.py
```

开启 bash 工具（可选）：

```bash
ENABLE_BASH_TOOL=1 python mini_agent_dashscope/stage07/main.py
```

## 验收

- 至少触发 2 个以上工具调用
- 如果开启 bash，能看到命令执行结果
