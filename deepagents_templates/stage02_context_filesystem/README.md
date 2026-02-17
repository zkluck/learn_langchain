# Stage 02: 上下文与虚拟文件系统

## 目标
- 理解 Deep Agent 如何把长上下文外置到文件系统。
- 学会用 `files` 预置输入文件。
- 体验同一 thread 下文件上下文的连续访问。

## 核心概念
- **Virtual Filesystem**：代理可通过 `read_file/write_file/edit_file` 管理上下文。
- **files 注入**：调用 `invoke` 时可预置虚拟文件。
- **thread_id**：同一会话下的状态与文件上下文可连续使用。

## 任务
1. 运行 `main.py`，观察 agent 先读需求再写 todo。
2. 修改预置需求文件内容，再运行对比输出。
3. 追加第二轮问题，验证同 thread 的文件可读性。

## 运行
```bash
uv run main.py
```

## 验收标准
- agent 能读取预置文件并完成写入任务。
- 第二轮提问能复用第一轮写入的文件。
