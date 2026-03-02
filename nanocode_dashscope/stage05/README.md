# Stage 05: 构造请求 Payload

在具备工具 schema 后，学习如何构造发送给 DashScope 的请求体，包含消息、模型、工具等字段。

## 目标

- 组装 `messages`、`model`、`tools`、`tool_choice` 字段
- 序列化为 JSON，验证格式与缩进
- 打印示例 payload，方便调试

## 运行

```bash
python main.py
```

## 预期输出

```
=== nanocode_dashscope Stage 05: 构造请求 Payload ===

--- 请求体 ---
{
  "model": "qwen3-max",
  "messages": [
    {
      "role": "user",
      "content": "请读取 README.md 的第一行"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "read",
        "description": "读取文件内容并显示行号",
        "parameters": {
          "type": "object",
          "properties": {
            "file_path": {
              "type": "string",
              "description": "要读取的文件路径"
            }
          },
          "required": [
            "file_path"
          ]
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```
