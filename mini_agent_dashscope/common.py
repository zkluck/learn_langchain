#!/usr/bin/env python3
"""
DashScope 教程公共函数
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> bool:  # type: ignore
        return False


# 预加载 .env，方便本地调试时直接生效
load_dotenv()


@dataclass
class DashScopeSettings:
    api_key: str
    base_url: str
    model: str


def configure_stdio() -> None:
    """保留终端编码，仅放宽错误处理，避免中文/emoji 输出报错。"""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="replace")
            except OSError:
                pass


def normalize_model(model: str) -> str:
    """兼容历史写法 openai:qwen3-max -> qwen3-max。"""
    value = model.strip()
    if value.startswith("openai:"):
        return value.split(":", 1)[1]
    return value


def normalize_base_url(base_url: str) -> str:
    """
    兼容两种写法：
    - .../v1
    - .../v1/chat/completions
    """
    url = base_url.strip().rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/v1"):
        return f"{url}/chat/completions"
    return url


def read_settings() -> DashScopeSettings:
    """读取环境变量并返回标准配置。"""
    api_key = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("DASHSCOPE_API_KEY")
        or ""
    ).strip()
    base_url = normalize_base_url(
        os.getenv(
            "OPENAI_BASE_URL",
            os.getenv(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            ),
        )
    )
    model = normalize_model(os.getenv("MODEL", "qwen3-max"))
    return DashScopeSettings(api_key=api_key, base_url=base_url, model=model)


def require_api_key(settings: DashScopeSettings) -> None:
    if not settings.api_key:
        raise RuntimeError("未检测到 API Key，请设置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY。")


def pretty_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def call_chat_completion(
    settings: DashScopeSettings,
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    tool_choice: Optional[str] = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    调用 DashScope OpenAI 兼容接口并返回 JSON。
    """
    payload: Dict[str, Any] = {
        "model": settings.model,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice

    request = urllib.request.Request(
        settings.base_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8") if error.fp else ""
        raise RuntimeError(f"HTTP {error.code}: {error.reason}\n{detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"网络错误: {error.reason}") from error
    except json.JSONDecodeError as error:
        raise RuntimeError(f"响应 JSON 解析失败: {error}") from error


def extract_assistant_text(response_json: Dict[str, Any]) -> str:
    """
    统一提取 assistant 文本，兼容空内容场景。
    """
    try:
        message = response_json["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return ""

    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if content is None:
        return ""
    # 少数模型可能返回结构化 content
    return str(content).strip()
