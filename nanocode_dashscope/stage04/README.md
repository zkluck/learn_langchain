# Stage 04: 工具 Schema 生成

将前面实现的工具描述为 JSON schema，便于 DashScope function calling 理解参数结构。

## 目标

- 定义 `read/write/edit/glob/grep/bash` 工具元数据
- 生成符合 OpenAI function calling 的 schema 列表
- 将 schema 序列化为 JSON，方便调试

## 运行

```bash
python main.py
```

## 预期输出

```
=== nanocode_dashscope Stage 04: 工具 Schema 生成 ===

工具数量: 6
[
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
  },
  ...
]
```
