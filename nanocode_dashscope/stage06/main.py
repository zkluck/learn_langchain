#!/usr/bin/env python3
"""
Stage 06: 调用 DashScope API
发送真实请求并打印响应/错误详情
"""

import json
import os
import sys
import urllib.request
import urllib.error
from dotenv import load_dotenv

# 预加载 .env 文件以便后续读取 API Key 等配置
load_dotenv()


def configure_stdio() -> None:
    """保留终端编码，仅放宽错误处理，避免中文/emoji 输出报错"""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="replace")
            except OSError:
                # 某些终端不支持重设参数，忽略即可
                pass


def normalize_base_url(base_url: str) -> str:
    """兼容两种地址写法：.../v1 或 .../chat/completions"""
    url = base_url.strip().rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/v1"):
        return f"{url}/chat/completions"
    return url


def normalize_model(model: str) -> str:
    """兼容历史写法 openai:qwen3-max -> qwen3-max"""
    value = model.strip()
    if value.startswith("openai:"):
        return value.split(":", 1)[1]
    return value

def build_messages():
    """构造示例对话消息列表"""
    # 这里给出一个简单问题，要求模型读取 README
    return [
        {
            "role": "user",
            "content": "请简要介绍 nanocode_dashscope 项目"
        }
    ]

def build_payload():
    """组装完整请求体"""
    # 允许通过环境变量自定义模型
    model = normalize_model(os.getenv("MODEL", "qwen3-max"))
    payload = {
        "model": model,
        "messages": build_messages(),
    }
    return payload

def call_api(payload):
    """调用 DashScope 兼容接口并返回 (状态码, 响应文本)"""
    base_url = normalize_base_url(
        os.getenv(
            "OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        )
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    # 将 payload 转为字节串以便 HTTP 发送
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    try:
        # 超时时间设置为 60 秒，避免长时间阻塞
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
            return response.status, body
    except urllib.error.HTTPError as error:
        # 读取错误详情，帮助定位权限或速率问题
        detail = error.read().decode("utf-8") if error.fp else ""
        raise RuntimeError(f"HTTP {error.code}: {error.reason}\n{detail}")
    except urllib.error.URLError as error:
        raise RuntimeError(f"网络错误: {error.reason}")

def main():
    """打印请求体并输出响应结果"""
    configure_stdio()
    print("=== nanocode_dashscope Stage 06: 调用 DashScope API ===\n")

    payload = build_payload()
    print("--- 请求体 ---")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    try:
        status, body = call_api(payload)
        print("\n--- 响应 ---")
        print(f"HTTP {status}")
        print(body)
    except RuntimeError as error:
        print("\n--- 错误 ---")
        print(str(error))
        print("请确认 API Key、模型、base_url 是否配置正确，并检查网络连通性。")
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
