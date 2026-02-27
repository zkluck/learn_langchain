## 1. 项目骨架与文档

- [x] 1.1 新建 `nanocode_dashscope/` 目录并初始化 README 结构（含目标、依赖、运行方式占位）
- [x] 1.2 在 README 中补充 DashScope API 说明、环境变量、示例命令

## 2. 工具层实现

- [x] 2.1 在 `nanocode.py` 中实现 `read/write/edit/glob/grep/bash` 工具并加注释
- [x] 2.2 构建 `TOOLS` 字典及 `make_schema`，确保 JSON schema 适配 DashScope function calling

## 3. DashScope API 接入

- [x] 3.1 实现 `call_api`：封装 base_url、鉴权 Header、默认模型以及错误处理
- [x] 3.2 支持环境变量覆盖（`DASHSCOPE_API_KEY`、`MODEL`、可选 `DASHSCOPE_BASE_URL`）并在 README 记录

## 4. 交互循环与体验

- [x] 4.1 编写主循环：维护对话历史、解析 `/c` `/q`、处理 tool_use 结果
- [x] 4.2 实现终端 UX（分隔线、颜色、工具结果预览、错误提示）并验证示例对话
