# Stage 06：MCP 集成

## 目标

- 掌握 MCP 配置与连接类型
- 学会处理连接与超时问题

## 实践步骤

1. 准备配置

- 复制 `mcp-example.json` 为 `mcp.json`
- 启用一个可用 server（建议先 `stdio`）

2. 配置超时参数

```yaml
tools:
  mcp:
    connect_timeout: 10.0
    execute_timeout: 60.0
    sse_read_timeout: 120.0
```

3. 启动 Agent 验证加载

- 观察 “Connected to MCP server” 日志
- 观察实际加载的 MCP tool 列表

## 关键知识点

- 支持连接类型：`stdio` / `sse` / `http` / `streamable_http`
- `mcp.json` 缺失时会尝试回退到 `mcp-example.json`
- 超时控制是防挂死关键，不要用默认无限等待

## 验收标准

- 至少加载 1 个 MCP 工具
- 能通过超时参数复现实验并解释结果

## 对应源码

- `mini_agent/tools/mcp_loader.py`
- `mini_agent/config/mcp-example.json`
