"""Stage 00: v1 环境与最小 Agent 示例。"""

import os

from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


# 这是一个最小工具函数：输入城市，返回天气文本。
def get_weather(city: str) -> str:
    """返回固定天气结果，用于学习工具调用流程。"""
    return f"{city} 晴，25C。"


# 这是第二个工具函数：做最基础的加法。
def add(a: float, b: float) -> float:
    """返回两个数字之和。"""
    return a + b


if __name__ == "__main__":
    # 自动读取项目根目录下的 .env 文件（如果存在）。
    # 这样新手只需要维护一个 .env 文件，不用每次手动 export。
    load_dotenv()

    # Agent 连接在线模型时需要 API Key。
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先在 .env 或环境变量中设置 OPENAI_API_KEY")

    # create_agent 是 LangChain v1 推荐入口。
    # model: 指定模型
    # tools: 模型可调用的工具列表
    # system_prompt: 系统级行为约束
    # qwen3-max 需要显式指定 provider；这里走 OpenAI 兼容协议。
    model = init_chat_model("qwen3-max", model_provider="openai")

    agent = create_agent(
        model=model,
        tools=[get_weather, add],
        system_prompt="你是一个简洁的助理。",
    )

    # messages 是对话输入，至少包含一条用户消息。
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "帮我查北京天气，并计算 13.5 + 7.2",
                }
            ]
        }
    )

    # 为了学习方便，先直接打印完整结果对象。
    print(result)
