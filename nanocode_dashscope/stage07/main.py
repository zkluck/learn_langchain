#!/usr/bin/env python3
"""
Stage 07: 基础对话循环
仅维护对话历史，不处理工具调用
"""

import json
import os
import urllib.error
import urllib.request

from typing import List, Dict


def call_api(messages: List[Dict[str, str]]) -> Dict[str, object]:
    """调用 DashScope API 并返回解析后的 JSON"""
    base_url = os.getenv(
        "OPENAI_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 未配置")

    # 构建请求体，携带当前对话历史
    payload = {
        "model": os.getenv("MODEL", "openai:qwen3-max"),
        "messages": messages,
    }

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
    raise SystemExit(main())
