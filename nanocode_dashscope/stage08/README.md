# Stage 08: 工具调用循环

在基础对话循环上加入工具调用：当 DashScope 返回 `tool_calls` 时，执行对应的本地工具并把结果反馈给模型。

## 目标

- 维护对话历史并解析 `tool_calls`
- 实现 `read/write/edit/glob/grep/bash` 工具并可被模型调用
- 将工具执行结果追加到 `messages` 中，再次请求模型生成最终回复

## 运行

```bash
export OPENAI_API_KEY="your-dashscope-api-key"
python main.py
```

## 交互示例

```
=== nanocode_dashscope Stage 08: 工具调用循环 ===

🤖 请输入问题 (输入 /c 清空历史, /q 退出):
> 读取 README.md 第一行

🔧 调用工具: read({"file_path": "README.md"})
✓ 工具结果(前 80 字符): # nanocode_dashscope

💬 模型回复:
我已读取 README.md，第一行是项目标题。
```

此阶段已具备基础代理功能，可执行文件与 shell 工具，并在终端展示工具调用情况。
