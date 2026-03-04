# Stage 07：双协议模型层

## 目标

- 理解 Anthropic/OpenAI 协议差异
- 掌握统一 LLM 包装层的扩展方式

## 实践步骤

1. 切换 provider 进行对比

```yaml
provider: "anthropic"
# provider: "openai"
```

2. 分别执行同一任务，比较：

- `thinking` 返回
- `tool_calls` 结构
- `usage` 字段

3. 阅读包装层

- `llm_wrapper.py`（统一入口）
- `anthropic_client.py` / `openai_client.py`（协议适配）

## 关键知识点

- MiniMax 域名会自动补协议路径后缀
- OpenAI 协议下 `reasoning_details` 的历史回传会影响后续推理连续性
- 统一 `LLMResponse` 是上层 Agent 无感切换的基础

## 验收标准

- 能解释为何主循环层不需要关心 provider 细节
- 能说明切换 provider 时需要关注哪些兼容项

## 对应源码

- `mini_agent/llm/llm_wrapper.py`
- `mini_agent/llm/anthropic_client.py`
- `mini_agent/llm/openai_client.py`
