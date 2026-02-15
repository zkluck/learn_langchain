"""Stage 08: normalize_priority 的基础测试。"""

from main import normalize_priority


# 正常输入：小写 p1 应转成标准值 P1。
def test_normalize_priority_ok() -> None:
    assert normalize_priority("p1") == "P1"


# 带空格输入：应先 trim 再转换。
def test_normalize_priority_trim() -> None:
    assert normalize_priority("  p2 ") == "P2"


# 非法输入：应回退到默认值 P3。
def test_normalize_priority_fallback() -> None:
    assert normalize_priority("urgent") == "P3"
