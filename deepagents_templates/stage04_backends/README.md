# Stage 04: Backends 路由

## 目标
- 理解 Deep Agents 的后端抽象（StateBackend / FilesystemBackend）。
- 对比“线程内状态文件”与“本地磁盘文件”两种存储策略。
- 学会为 FilesystemBackend 开启 `virtual_mode=True`。

## 核心概念
- **StateBackend**：默认后端，文件存在 agent state 中，适合会话级上下文。
- **FilesystemBackend**：真实落盘，适合本地开发工具链。
- **virtual_mode=True**：限制路径在 root_dir 内，降低越权风险。

## 任务
1. 运行 `main.py`，观察两种 backend 的执行差异。
2. 查看 stage 目录下 `workspace/` 的实际文件产物。
3. 把 root_dir 改成你自己的临时目录再试一次。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能解释 StateBackend 与 FilesystemBackend 的适用边界。
- 能验证 FilesystemBackend 的真实文件落盘。
