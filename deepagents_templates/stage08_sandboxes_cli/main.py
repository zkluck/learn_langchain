"""Stage 08: Sandboxes + CLI。

按环境变量 DEEPAGENTS_SANDBOX 选择 provider：
- daytona
- runloop
- modal
"""

import os
from typing import Callable

from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI


def require_model_key() -> None:
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("请先设置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY")


def resolve_model():
    model = os.getenv("DEEPAGENTS_MODEL", "openai:qwen3-max")
    if model.startswith("openai:"):
        return ChatOpenAI(model=model.split(":", 1)[1], use_responses_api=False)
    return model


def build_sandbox_backend() -> tuple[object, Callable[[], None]]:
    provider = os.getenv("DEEPAGENTS_SANDBOX", "").strip().lower()

    if provider == "daytona":
        from daytona import Daytona
        from langchain_daytona import DaytonaSandbox

        sandbox = Daytona().create()
        backend = DaytonaSandbox(sandbox=sandbox)
        return backend, sandbox.stop

    if provider == "runloop":
        from runloop_api_client import RunloopSDK
        from langchain_runloop import RunloopSandbox

        api_key = os.getenv("RUNLOOP_API_KEY")
        if not api_key:
            raise RuntimeError("使用 runloop 需要 RUNLOOP_API_KEY")

        client = RunloopSDK(bearer_token=api_key)
        devbox = client.devbox.create()
        backend = RunloopSandbox(devbox=devbox)
        return backend, devbox.shutdown

    if provider == "modal":
        import modal
        from langchain_modal import ModalSandbox

        app_name = os.getenv("MODAL_APP_NAME")
        if not app_name:
            raise RuntimeError("使用 modal 需要设置 MODAL_APP_NAME")

        app = modal.App.lookup(app_name)
        modal_sandbox = modal.Sandbox.create(app=app)
        backend = ModalSandbox(sandbox=modal_sandbox)
        return backend, modal_sandbox.terminate

    raise RuntimeError(
        "请设置 DEEPAGENTS_SANDBOX=daytona|runloop|modal，并安装对应依赖。"
    )


def main() -> None:
    load_dotenv()
    require_model_key()

    backend, cleanup = build_sandbox_backend()
    model = resolve_model()

    try:
        agent = create_deep_agent(
            model=model,
            backend=backend,
            system_prompt=(
                "你是 Python 助手。请在沙箱里创建最小脚本并执行，"
                "最后给出执行结果摘要。"
            ),
        )

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "请创建 hello.py，内容是打印 'Hello Deep Agents'，"
                            "再执行 python hello.py，并汇报输出。"
                        ),
                    }
                ]
            }
        )

        print("=== Stage 08 Result ===")
        print(result["messages"][-1].content)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
