# Stage 00：环境与配置

## 目标

- 跑通 Mini-Agent 的本地环境
- 完成 API 配置
- 理解配置文件查找优先级

## 前置条件

- Python 3.10+
- 已安装 `uv`
- 可用 MiniMax API Key

## 实践步骤

1. 克隆仓库并安装依赖

```bash
git clone https://github.com/MiniMax-AI/Mini-Agent.git
cd Mini-Agent
uv sync
```

2. 生成配置文件（Windows）

```powershell
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/MiniMax-AI/Mini-Agent/main/scripts/setup-config.ps1" -OutFile "$env:TEMP\setup-config.ps1"
powershell -ExecutionPolicy Bypass -File "$env:TEMP\setup-config.ps1"
```

3. 编辑 `~/.mini-agent/config/config.yaml`

```yaml
api_key: "YOUR_API_KEY"
api_base: "https://api.minimax.io"
model: "MiniMax-M2.5"
provider: "anthropic"
```

## 关键知识点

- 配置优先级：
  1. `./mini_agent/config/config.yaml`
  2. `~/.mini-agent/config/config.yaml`
  3. 安装包内 `mini_agent/config/config.yaml`
- MiniMax 域名会根据 provider 自动补后缀：
  - `anthropic` -> `/anthropic`
  - `openai` -> `/v1`

## 验收标准

- 配置文件加载成功
- API Key 不是占位符
- 能解释上述 3 层配置优先级

## 对应源码

- `mini_agent/config.py`
- `scripts/setup-config.ps1`
