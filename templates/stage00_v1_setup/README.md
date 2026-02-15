# Stage 00: v1 环境与最小 Agent

## 目标
- 跑通 LangChain v1 的最小 Agent。
- 理解 `model`、`tools`、`system_prompt` 三个关键参数。

## 任务
1. 安装依赖并配置 API Key。
2. 运行 `main.py`，确认工具可被调用。
3. 新增一个你自己的工具函数并让模型调用。

## API Key（推荐 .env）
在项目根目录创建 `.env` 文件：

```bash
echo 'OPENAI_API_KEY=你的key' > .env
```

## 运行
```bash
uv run python templates/stage00_v1_setup/main.py
```

## 验收标准
- 成功输出模型结果。
- 至少看到一次工具调用生效。
