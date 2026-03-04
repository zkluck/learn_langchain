#!/usr/bin/env python3
"""
Stage 00: DashScope 环境检查
"""

from __future__ import annotations

import sys
from pathlib import Path

# 允许从上级目录导入公共模块
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import configure_stdio, pretty_json, read_settings


def main() -> int:
    configure_stdio()
    settings = read_settings()

    masked_key = (
        f"{settings.api_key[:6]}...{settings.api_key[-4:]}"
        if settings.api_key
        else "(未配置)"
    )
    result = {
        "api_key": masked_key,
        "base_url": settings.base_url,
        "model": settings.model,
        "ready": bool(settings.api_key),
        "tips": [
            "API Key 读取优先级: OPENAI_API_KEY > DASHSCOPE_API_KEY",
            "BASE_URL 支持 .../v1 或 .../chat/completions，两者会自动兼容",
        ],
    }

    print("=== mini_agent_dashscope Stage 00: 环境检查 ===")
    print(pretty_json(result))

    if not settings.api_key:
        print("\n未检测到 API Key，请先配置 OPENAI_API_KEY。")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
