# Stage 09: 完整示例汇总

集成所有功能的完整 agentic loop 实现，展示如何与 DashScope 进行多轮对话和工具调用。

## 目标

- 集成所有工具：read、write、edit、glob、grep、bash
- 实现完整的对话循环，支持工具调用
- 提供友好的终端交互界面
- 演示实际使用场景

## 功能特性

- **多轮对话**: 维护完整的对话历史
- **工具调用**: 自动解析和执行模型返回的工具调用
- **错误处理**: 完善的错误提示和恢复机制
- **终端界面**: 清晰的输出格式和颜色支持

## 运行

```bash
# 设置环境变量
export OPENAI_API_KEY="your-dashscope-api-key"

# 启动交互式代理
python main.py

# 输入示例：
# "读取当前目录的 README.md 文件"
# "创建一个包含当前日期的文件"
# "列出所有 Python 文件"
# "/c" - 清空对话历史
# "/q" - 退出程序
```

## 预期交互示例

```
=== nanocode_dashscope Stage 09: 完整代理 ===

🤖 输入你的问题 (输入 /c 清空历史, /q 退出):
> 读取 README.md 文件

🔧 调用工具: read(file_path="README.md")
✓ 工具执行成功

📝 README.md 内容:
1: # nanocode_dashscope
2: 
3: 分阶段 Python 教程...

💬 模型回复:
我已经读取了 README.md 文件。这是一个分阶段 Python 教程项目，展示了如何使用 DashScope 构建代理循环...

🤖 输入你的问题 (输入 /c 清空历史, /q 退出):
> /q

👋 再见！
```
