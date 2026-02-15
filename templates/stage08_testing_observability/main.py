"""Stage 08: 供测试使用的示例函数。"""


def normalize_priority(label: str) -> str:
    """把输入优先级标准化为 P1/P2/P3。"""
    # strip(): 去掉首尾空格；upper(): 统一转大写。
    normalized = label.strip().upper()

    # 不在允许值中的输入，统一降级到 P3。
    if normalized not in {"P1", "P2", "P3"}:
        return "P3"
    return normalized
