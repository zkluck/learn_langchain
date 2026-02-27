# Stage 07: 基础对话循环

实现最简单的 REPL，维护用户输入和模型回复，但暂不处理工具调用。

## 目标

- 构建命令行循环，支持 `/c` 清空历史、`/q` 退出
- 维护 `messages` 列表并发送给 DashScope API
- 打印模型回复，保留上下文

## 运行

```bash
export OPENAI_API_KEY="your-dashscope-api-key"
python main.py
```

```powershell
$env:OPENAI_API_KEY="your-dashscope-api-key"
python main.py
```

## 预期交互

```
=== nanocode_dashscope Stage 07: 基础对话循环 ===

[INFO] 请输入问题 (输入 /c 清空历史, /q 退出):
> 你好

[ASSISTANT] 模型回复:
你好！有什么可以帮忙的吗？

[INFO] 请输入问题 (输入 /c 清空历史, /q 退出):
> /c

[OK] 对话历史已清空
```
