# Stage 05: 长期记忆

## 目标
- 搭建“短期 + 长期”双层存储。
- 使用 `CompositeBackend` 将 `/memories/` 路由到持久化 store。
- 体验跨 thread 的记忆复用。

## 核心概念
- **CompositeBackend**：按路径把文件路由到不同后端。
- **StateBackend**：短期上下文（会话内）。
- **StoreBackend**：长期持久化（可跨 thread）。

## 任务
1. 运行 `main.py`，先写入 `/memories/user_profile.md`。
2. 在另一个 thread 中让 agent 读取并复述该记忆。
3. 尝试增加第二个记忆文件（如 `/memories/project_rules.md`）。

## 运行
```bash
uv run main.py
```

## 验收标准
- 同一 agent 的不同 thread 可读到持久化 memory。
- 能解释为什么 `/memories/` 路径可跨 thread 生效。
