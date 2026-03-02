#!/usr/bin/env python3
"""
Stage 07: 基础对话循环
仅维护对话历史，不处理工具调用
"""

import json
import os
import sys
import urllib.error
import urllib.request

from typing import List, Dict
from dotenv import load_dotenv


def configure_stdio() -> None:
    """保留终端编码，仅放宽错误处理，避免 emoji 输出报错"""
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


def call_api(messages: List[Dict[str, str]]) -> Dict[str, object]:
    """调用 DashScope API 并返回解析后的 JSON"""
    base_url = normalize_base_url(
        os.getenv(
            "OPENAI_BASE_URL",
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        )
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    # 构建请求体，携带当前对话历史
    model = normalize_model(os.getenv("MODEL", "qwen3-max"))
    payload = {"model": model, "messages": messages}

    # 将 JSON 序列化为字节流以便发送
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base_url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        # 输出 DashScope 返回的错误内容，方便调试
        detail = error.read().decode("utf-8") if error.fp else ""
        raise RuntimeError(f"HTTP {error.code}: {error.reason}\n{detail}")
    except urllib.error.URLError as error:
        raise RuntimeError(f"网络错误: {error.reason}")


def main() -> int:
    """简单的命令行对话循环"""
    configure_stdio()
    print("=== nanocode_dashscope Stage 07: 基础对话循环 ===\n")

    if not os.getenv("OPENAI_API_KEY"):
        print("错误: 请先设置 OPENAI_API_KEY 环境变量")
        return 1

    messages: List[Dict[str, str]] = []
    print("[INFO] 请输入问题 (输入 /c 清空历史, /q 退出):")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] 再见！")
            break

        if not user_input:
            continue
        if user_input == "/q":
            print("\n[INFO] 再见！")
            break
        if user_input == "/c":
            messages.clear()
            print("\n[OK] 对话历史已清空")
            continue

        # 追加用户消息
        messages.append({"role": "user", "content": user_input})

        try:
            response = call_api(messages)
        except RuntimeError as error:
            print(f"\n[ERR] 调用失败: {error}")
            messages.pop()  # 删除导致失败的消息，避免阻塞后续对话
            continue

        assistant_message = response["choices"][0]["message"]
        messages.append(assistant_message)
        print("\n[ASSISTANT] 模型回复:")
        print(assistant_message.get("content", "(无内容)"))

    return 0


if __name__ == "__main__":
    # 预加载 .env 文件以便后续读取 API Key 等配置
    load_dotenv()

    raise SystemExit(main())
