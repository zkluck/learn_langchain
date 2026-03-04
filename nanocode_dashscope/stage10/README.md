# Stage 10: LangGraph 完整代理

在 Stage 09 手写 agentic loop 的基础上，改用 LangGraph 实现同等能力：

- 完整多轮对话
- 自动工具调用（read / write / edit / glob / grep / bash）
- `/c` 清空历史、`/q` 退出
- 工具调用上限保护，避免死循环

## 目标

- 理解 `StateGraph(MessagesState)` 的消息状态管理方式
- 理解 `ToolNode + tools_condition` 的自动工具循环
- 对比手写循环（Stage 09）与图式编排（Stage 10）的实现差异

## 图结构

```text
START -> model -> (有 tool_calls ?) -> tools -> model -> ... -> END
```

- `model` 节点：调用 `ChatOpenAI(...).bind_tools(tools)`
- `tools` 节点：由 `ToolNode` 自动执行工具
- 条件边：`tools_condition` 决定是否继续走工具链

## 运行

```bash
export OPENAI_API_KEY="your-dashscope-api-key"
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
export MODEL="qwen3-max"
# 可选，默认关闭
export ENABLE_BASH_TOOL="0"

python main.py
# 或
uv run main.py
```

```powershell
$env:OPENAI_API_KEY="your-dashscope-api-key"
$env:OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
$env:MODEL="qwen3-max"
$env:ENABLE_BASH_TOOL="0"

python main.py
# 或
uv run main.py
```

## 预期交互

```text
=== nanocode_dashscope Stage 10: LangGraph 完整代理 ===

[INFO] 输入你的问题 (输入 /c 清空历史, /q 退出):
> 创建一个 a.txt 文件，内容是你好

[TOOL] 调用工具: write({"file_path":"a.txt","content":"你好"})
[OK] 工具执行结果: [OK] 写入文件: a.txt

[ASSISTANT] 模型回复:
已在当前目录创建 a.txt 文件，并写入内容“你好”。
```

## 常见问题

- `401 Unauthorized`: 检查 `OPENAI_API_KEY`
- `404/model_not_found`: 检查 `OPENAI_BASE_URL` 和 `MODEL`
- 工具调用过多被中断：脚本会显示“超过上限”，可优化提示词减少来回调用
- `bash` 工具不可用：需设置 `ENABLE_BASH_TOOL=1`

