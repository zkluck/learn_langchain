# Stage 07: RAG + MCP

## 目标
- 先完成一个最小 2-step RAG。
- 再把 MCP 资源/工具接入同一工作流。

## 任务
1. 运行 `main.py` 的本地检索示例。
2. 把你的文档放入 `docs/` 并扩充检索逻辑。
3. 在 README 中补上你使用的 MCP 服务与用途。

## 运行
```bash
uv run python templates/stage07_rag_mcp/main.py
```

## 验收标准
- 问题能引用本地资料作答。
- 至少完成 1 个 MCP 接入尝试（可先 stub）。
