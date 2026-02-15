# Stage 04: Memory 与 State

## 目标
- 在同一 `thread_id` 下保持上下文连续。
- 能读写最小用户偏好状态。

## 任务
1. 运行 `main.py`，比较同/不同 `thread_id` 的回答差异。
2. 新增一个用户偏好字段（比如语言、城市）。
3. 用工具读取偏好并用于最终回答。

## 运行
```bash
uv run python templates/stage04_memory_state/main.py
```

## 验收标准
- 同 `thread_id` 能“记住”，不同 `thread_id` 能隔离。
