# Stage 03：基础工具体系

## 目标

- 理解 Tool 协议统一接口
- 掌握文件工具与 Bash 工具

## 实践步骤

1. 跑示例

```bash
uv run python examples/01_basic_tools.py
uv run python examples/02_simple_agent.py
```

2. 手动验证文件工具

- `read_file`
- `write_file`
- `edit_file`

3. 手动验证 shell 工具

- `bash` 前台命令
- `bash` 后台命令（`run_in_background=true`）
- `bash_output` 轮询输出
- `bash_kill` 终止进程

## 关键知识点

- Tool 需提供：
  - `name`
  - `description`
  - `parameters`（JSON Schema）
  - `execute()`
- `to_schema()` 与 `to_openai_schema()` 是跨协议适配关键
- `read_file` 默认返回带行号内容，便于精确编辑

## 验收标准

- 能写一个最小自定义工具并运行
- 能完整演示后台任务启动、查看输出、终止

## 对应源码

- `mini_agent/tools/base.py`
- `mini_agent/tools/file_tools.py`
- `mini_agent/tools/bash_tool.py`
