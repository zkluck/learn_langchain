# Stage 00: Hello Deep Agent

## 目标
- 跑通第一个 Deep Agent。
- 理解 `create_deep_agent` 的最小参数：model / tools / system_prompt。
- 熟悉 Deep Agent 的输入输出格式（`messages`）。

## 核心概念
- **Deep Agent**：内置规划、文件系统与任务委派能力的代理。
- **工具函数**：普通 Python 函数即可作为工具暴露给模型。
- **invoke 输入**：与 LangChain/LangGraph 一样，使用 `{"messages": [...]}`。

## 任务
1. 运行 `main.py`。
2. 修改工具函数返回值，观察回答变化。
3. 改 system prompt，观察代理风格变化。

## 运行
```bash
uv run main.py
```

## 验收标准
- 成功得到一条由模型生成的最终回答。
- 理解 Deep Agent 的最小调用路径。
