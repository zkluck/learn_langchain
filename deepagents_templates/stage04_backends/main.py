"""Stage 04: Backends 对比。"""

import os
from pathlib import Path

from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_openai import ChatOpenAI


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

    # 1) 默认 StateBackend
    state_agent = create_deep_agent(
        model=model,
        system_prompt="你是项目助理，优先用文件管理中间结果。",
    )

    state_result = state_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请在虚拟文件系统写入 /notes/state_backend.md，"
                        "内容是 3 条 Deep Agents 学习建议，然后再读取并总结。"
                    ),
                }
            ]
        }
    )

    print("=== Stage 04: StateBackend ===")
    print(state_result["messages"][-1].content)

    # 2) FilesystemBackend
    workspace = Path(__file__).resolve().parent / "workspace"
    workspace.mkdir(parents=True, exist_ok=True)

    fs_agent = create_deep_agent(
        model=model,
        backend=FilesystemBackend(root_dir=str(workspace), virtual_mode=True),
        system_prompt="你是项目助理，写文件后请说明写入了哪些路径。",
    )

    fs_result = fs_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请写入 /backend_demo.md，内容包含 3 条后端选型建议，"
                        "然后读取该文件并给我结论。"
                    ),
                }
            ]
        }
    )

    print("\n=== Stage 04: FilesystemBackend ===")
    print(fs_result["messages"][-1].content)

    host_file = workspace / "backend_demo.md"
    print("\n=== Host File Check ===")
    print(f"exists={host_file.exists()} path={host_file}")
    if host_file.exists():
        print(host_file.read_text(encoding="utf-8")[:300])


if __name__ == "__main__":
    main()
