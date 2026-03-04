#!/usr/bin/env python3
"""
Stage 08: MCP 配置助手（DashScope）
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common import configure_stdio, read_settings


def backup_if_exists(path: Path) -> None:
    if not path.exists():
        return
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = path.with_suffix(path.suffix + f".bak.{stamp}")
    shutil.copy2(path, bak)
    print(f"已备份: {bak}")


def build_mcp_config(enable_search: bool) -> Dict[str, Any]:
    settings = read_settings()
    jina = os.getenv("JINA_API_KEY", "").strip()
    serper = os.getenv("SERPER_API_KEY", "").strip()
    minimax = os.getenv("MINIMAX_API_KEY", "").strip() or settings.api_key

    has_all_keys = bool(jina and serper and minimax)
    should_enable = enable_search and has_all_keys

    return {
        "mcpServers": {
            "minimax_search": {
                "description": "MiniMax Search - Web search and browse",
                "type": "stdio",
                "command": "uvx",
                "args": [
                    "--from",
                    "git+https://github.com/MiniMax-AI/minimax_search",
                    "minimax-search",
                ],
                "env": {
                    "JINA_API_KEY": jina,
                    "SERPER_API_KEY": serper,
                    "MINIMAX_API_KEY": minimax,
                },
                "disabled": not should_enable,
            },
            "memory": {
                "description": "MCP memory server",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-memory"],
                "disabled": True,
            },
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 Mini-Agent MCP 配置")
    parser.add_argument("--enable-search", action="store_true", help="尝试启用 minimax_search（需完整 key）")
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在 mcp.json（会先备份）")
    args = parser.parse_args()

    configure_stdio()
    config_dir = Path.home() / ".mini-agent" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    mcp_path = config_dir / "mcp.json"

    if mcp_path.exists() and not args.overwrite:
        print(f"已存在: {mcp_path}")
        print("如需覆盖请使用 --overwrite")
        return 0

    backup_if_exists(mcp_path)
    payload = build_mcp_config(enable_search=args.enable_search)
    mcp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    search_disabled = payload["mcpServers"]["minimax_search"]["disabled"]
    print("=== mini_agent_dashscope Stage 08: MCP 配置完成 ===")
    print(f"mcp: {mcp_path}")
    print(f"minimax_search enabled: {not search_disabled}")
    if search_disabled and args.enable_search:
        print("提示：你传了 --enable-search，但缺少 JINA_API_KEY / SERPER_API_KEY / MINIMAX_API_KEY，已自动禁用。")
    print("下一步可执行: mini-agent --task \"请用搜索工具总结今天的 AI 新闻\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
