"""Stage 05: 中间件思路演示（模型调用前后统一处理）。"""

import os
from typing import Any

from langchain.agents import create_agent


# 说明：不同版本中 middleware 接口名称可能有细微差异。
# 该模板用于学习“在模型调用前后做统一处理”的思路。

def before_model(state: dict[str, Any]) -> dict[str, Any]:
    """模型调用前执行：打印当前消息数量。"""
    messages = state.get("messages", [])
    print(f"[before_model] message_count={len(messages)}")
    return state


def after_model(state: dict[str, Any]) -> dict[str, Any]:
    """模型调用后执行：打印当前消息数量。"""
    messages = state.get("messages", [])
    print(f"[after_model] message_count={len(messages)}")
    return state


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY")

    # middleware 列表里可放多个处理函数。
    agent = create_agent(
        model="openai:qwen3-max",
        tools=[],
        system_prompt="你是中间件实验助手。",
        middleware=[before_model, after_model],
    )

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "写一句简短的系统健康检查结论。"}
            ]
        }
    )
    print(result)
