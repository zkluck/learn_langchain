# nanocode_dashscope

分阶段 Python 教程，演示使用 DashScope OpenAI 兼容接口构建 agentic loop（工具、schema、API 调用、对话循环）。

## 目标

- 提供逐步可运行的 Python 示例（stage00–stage10），每阶段独立可运行
- 展示工具实现、schema 生成、API 调用、对话循环的演进过程
- 与 LangGraph/LangChain 模板对照，帮助理解底层实现

## 环境变量

```bash
# 必需
export OPENAI_API_KEY="your-dashscope-api-key"

# 可选
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
export MODEL="qwen3-max"

# 可选（默认关闭 shell 工具，建议按需开启）
export ENABLE_BASH_TOOL="0"
```

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="your-dashscope-api-key"
$env:OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
$env:MODEL="qwen3-max"
$env:ENABLE_BASH_TOOL="0"
```

## 兼容说明

- `OPENAI_BASE_URL`：stage06/stage07/stage08/stage09 同时兼容以下两种写法
  - `https://dashscope.aliyuncs.com/compatible-mode/v1`
  - `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions`
- `MODEL`：推荐使用 `qwen3-max`；如果配置为历史写法 `openai:qwen3-max`，stage06/stage07/stage08/stage09 会自动转换

## 运行方式

```bash
# 进入任意阶段目录
cd nanocode_dashscope/stage00

# 方式 1：直接运行
python main.py

# 方式 2：使用 uv（推荐）
uv run main.py
```

## 目录结构

```
nanocode_dashscope/
├── README.md           # 本文件
├── stage00/            # 环境检查
├── stage01/            # 工具实现：文件读写
├── stage02/            # 工具实现：文件编辑
├── stage03/            # 工具实现：shell 命令
├── stage04/            # schema 生成
├── stage05/            # payload 构造
├── stage06/            # API 调用
├── stage07/            # 基础对话循环
├── stage08/            # 带工具的对话循环
├── stage09/            # 完整示例汇总（手写循环）
└── stage10/            # 完整示例汇总（LangGraph 实现）
```

## 常见错误

- **401 Unauthorized**: 检查 `OPENAI_API_KEY` 是否正确
- **404 Not Found / model_not_found**: 检查 `OPENAI_BASE_URL` 和 `MODEL` 配置，推荐 `MODEL=qwen3-max`
- **JSONDecodeError**: 通常是上游返回了空响应或非 JSON 内容；stage08 已增强错误提示，会显示响应预览帮助排查
- **超时**: 网络问题或模型响应慢，可重试
- **Windows 控制台乱码/报错**: 建议使用 PowerShell，必要时执行 `chcp 65001`

## 依赖

- Python 3.11+
- `python-dotenv`
- 其余逻辑主要使用标准库：`urllib.request`、`json`、`pathlib`、`subprocess`、`glob`
