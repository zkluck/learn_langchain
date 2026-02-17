"""Stage 00: Hello Deep Agent — 最小可运行示例。"""

import os

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI


def city_weather(city: str) -> str:
    """模拟天气工具。"""
    mapping = {
        "北京": "晴，24C",
        "上海": "多云，22C",
        "深圳": "小雨，28C",
    }
    return mapping.get(city, f"{city}: 暂无天气数据")


def require_model_key() -> None:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")


def resolve_model():
    model = os.getenv("DEEPAGENTS_MODEL", "openai:qwen3-max")
    if model.startswith("openai:"):
        return ChatOpenAI(model=model.split(":", 1)[1], use_responses_api=False)
    return model


def main() -> None:
    load_dotenv()
    require_model_key()

    model = resolve_model()

    agent = create_deep_agent(
        model=model,
        tools=[city_weather],
        system_prompt="你是一个简洁助手。回答前可使用工具核对事实。",
    )

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "北京今天天气如何？顺便给我一句出行建议。"}
            ]
        }
    )

    print("=== Stage 00 Result ===")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
