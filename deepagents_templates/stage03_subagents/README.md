# Stage 03: 子代理（Subagents）

## 目标
- 学会配置 specialized subagent。
- 理解主代理通过 `task` 委派复杂子任务的模式。
- 体验“主代理编排 + 子代理深挖”的协作结构。

## 核心概念
- **SubAgent（字典配置）**：通过 name/description/system_prompt/tools 定义。
- **Context Isolation**：子代理在独立上下文执行，最后只回传结果。
- **主代理路由**：根据问题复杂度决定是否委派。

## 任务
1. 运行 `main.py`，观察研究类问题的输出。
2. 修改 subagent 的 description，观察调用效果变化。
3. 增加一个第二子代理（如 code-reviewer）。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能完成主代理 + 子代理协作的一次完整调用。
- 能解释 subagent 的配置字段作用。
