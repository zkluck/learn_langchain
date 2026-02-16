# Stage 01: State 设计

## 目标
- 理解 LangGraph 中 State 的作用：节点间的共享数据结构。
- 掌握 TypedDict 和 Pydantic 两种定义方式。
- 学会使用 Reducer（追加 vs 覆盖）管理列表类字段。

## 核心概念
- **State**：图执行期间所有节点共享的"内存"，每个节点读取 state、返回要更新的字段。
- **Reducer**：决定"多次写入同一字段"时如何合并。默认是覆盖；对消息列表通常用 `operator.add` 做追加。
- **MessagesState**：LangGraph 内置的快捷 State，自带 `messages` 字段 + 追加 reducer。

## 任务
1. 运行 `main.py`，观察不同 state 定义方式的行为差异。
2. 尝试给 State 添加新字段，观察节点如何读写。
3. 修改 reducer，对比覆盖和追加的区别。

## 运行
```bash
uv run main.py
```

## 验收标准
- 能解释 TypedDict State 和 Pydantic State 的区别。
- 理解 Reducer 的作用，能正确使用 `Annotated[list, operator.add]`。
