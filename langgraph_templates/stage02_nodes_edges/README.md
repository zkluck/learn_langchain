# Stage 02: Nodes 与 Edges

## 目标
- 掌握多节点图的构建。
- 理解普通边（add_edge）与条件边（add_conditional_edges）。
- 学会用路由函数实现分支逻辑。

## 核心概念
- **Normal Edge**：`add_edge("a", "b")` — 固定从 a 到 b。
- **Conditional Edge**：`add_conditional_edges("a", routing_fn)` — 根据 state 动态选择下一个节点。
- **Entry Point**：`add_edge(START, "first_node")` — 指定入口节点。

## 任务
1. 运行 `main.py`，观察条件分支的路由行为。
2. 修改路由函数，增加一个新的分支。
3. 尝试让同一个节点根据不同输入走不同路径。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能画出图的流向（哪些节点连哪些边）。
- 理解条件边的路由函数如何决定下一步。
