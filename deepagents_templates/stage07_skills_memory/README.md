# Stage 07: Skills + Memory 文件

## 目标
- 使用 `SKILL.md` 封装可复用能力。
- 使用 `AGENTS.md` 作为持续上下文记忆。
- 理解 skill（按需加载）与 memory（总是加载）的差异。

## 核心概念
- **Skills**：渐进式加载，按任务需要注入。
- **Memory**：始终可见，适合稳定偏好与规则。
- **FilesystemBackend**：便于在本地项目直接管理 skills/memory 文件。

## 任务
1. 运行 `main.py`，观察回答是否遵循 AGENTS.md 的风格约束。
2. 修改 `skills/langgraph-docs/SKILL.md` 的说明，再运行对比。
3. 在 AGENTS.md 新增一条团队规则并验证生效。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能说清 skill 与 memory 的加载机制差异。
- 回答风格明显受 AGENTS.md 约束。
