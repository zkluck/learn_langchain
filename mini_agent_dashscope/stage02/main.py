#!/usr/bin/env python3
"""
Stage 02: DashScope 连通性测试
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import (
    call_chat_completion,
    configure_stdio,
    extract_assistant_text,
    pretty_json,
    read_settings,
    require_api_key,
)


def main() -> int:
    configure_stdio()
    settings = read_settings()
    try:
        require_api_key(settings)
    except RuntimeError as error:
        print(error)
        return 1

    messages = [
        {
            "role": "user",
            "content": "请仅回复 PONG（大写）。",
        }
    ]

    print("=== mini_agent_dashscope Stage 02: API 连通性测试 ===")
    print(f"model={settings.model}")
    print(f"base_url={settings.base_url}")

    try:
        response_json = call_chat_completion(settings=settings, messages=messages, timeout=60)
    except RuntimeError as error:
        print("\n请求失败：")
        print(error)
        return 1

    answer = extract_assistant_text(response_json)
    usage = response_json.get("usage")

    print("\n--- assistant ---")
    print(answer or "(空)")
    if usage:
        print("\n--- usage ---")
        print(pretty_json(usage))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
