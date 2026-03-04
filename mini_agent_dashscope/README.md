# mini_agent_dashscope

分阶段教程代码：使用 DashScope（OpenAI 兼容接口）驱动一个“Mini-Agent 风格”的本地工具循环。

统一手册（建议从这里开始）：
- `mini_agent_dashscope/UNIFIED_STAGE_GUIDE.md`
- 理论文档目录：`mini_agent_dashscope/docs/`

## 目标

- 用最少依赖跑通 DashScope 调用
- 学会 function calling + 工具执行循环
- 平滑迁移到 `mini-agent` CLI

## 环境变量

```bash
# 必需（任选其一，优先读 OPENAI_API_KEY）
export OPENAI_API_KEY="your-dashscope-api-key"
# export DASHSCOPE_API_KEY="your-dashscope-api-key"

# 可选
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
export MODEL="qwen3-max"
```

```powershell
$env:OPENAI_API_KEY="your-dashscope-api-key"
$env:OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
$env:MODEL="qwen3-max"
```

## 目录

```text
mini_agent_dashscope/
  common.py
  docs/
  stage00/
  stage01/
  stage02/
  stage03/
  stage04/
  stage05/
  stage06/
  stage07/
  stage08/
  stage09/
  stage10/
```

## 学习顺序

1. `stage00`：检查配置
2. `stage01`：生成 Mini-Agent 配置文件（DashScope 版）
3. `stage02`：连通性测试（真实 API 调用）
4. `stage03`：通过 `mini-agent --task` 跑单任务
5. `stage04`：手写工具调用循环（核心代码）
6. `stage05`：端到端验收脚本
7. `stage06`：记忆工具循环（record/recall）
8. `stage07`：全工具循环（含可选 bash）
9. `stage08`：MCP 配置助手
10. `stage09`：mini-agent 日志回放分析
11. `stage10`：进阶总验收

## 运行

```bash
cd mini_agent_dashscope/stage00
python main.py
```

或：

```bash
uv run mini_agent_dashscope/stage00/main.py
```
