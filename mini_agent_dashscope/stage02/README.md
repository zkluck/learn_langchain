# Stage 02：DashScope 连通性测试

## 目标

- 发送真实请求到 DashScope
- 验证 `model/base_url/api_key` 是否有效

## 运行

```bash
python mini_agent_dashscope/stage02/main.py
```

## 验收

- 返回 assistant 文本
- 输出 usage（若接口返回）
