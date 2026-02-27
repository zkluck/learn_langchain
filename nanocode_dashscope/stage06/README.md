# Stage 06: 调用 DashScope API

在构造好 payload 后，真正向 DashScope 兼容接口发送请求并打印响应结果。

## 目标

- 使用 `urllib.request` 发送 POST 请求
- 读取 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL` 环境变量
- 打印 HTTP 状态、返回内容、错误信息

## 运行

```bash
export OPENAI_API_KEY="your-dashscope-api-key"
python main.py
```

```powershell
$env:OPENAI_API_KEY="your-dashscope-api-key"
python main.py
```

## 预期输出

```
=== nanocode_dashscope Stage 06: 调用 DashScope API ===

--- 请求体 ---
{...}

--- 响应 ---
HTTP 200
{
  "id": "...",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "..."
      }
    }
  ]
}
```

若发生错误（例如 401、429），程序会打印错误详情和可能的解决建议。
