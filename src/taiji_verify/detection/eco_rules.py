"""
Eco Rules - 生态环境规则

从 wfgy.js 迁移的5条规则 (R001, R003-R006)

表格:
ID  名称        匹配              验证                置信度
R001 假标准编号  GB编号正则        编号>9999          0.95
R003 时间穿越    未来年份          年份>当前年        0.90
R004 自相矛盾    矛盾词            正反义同时出现     0.92
R005 错误法律状态 法典状态          说"未颁布"         0.95
R006 虚假历史    历史年份          说"2025年发布"     0.90

每条规则: pattern + check(text,match) + correction(match,text) + base_confidence
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional
from datetime import datetime


@dataclass
class EcoRule:
    """生态环境规则"""

    id: str
    name: str
    pattern: str
    check: Callable[[str, Optional[re.Match]], bool]
    correction: Callable[[Optional[re.Match], str], str]
    base_confidence: float


class FakeStandardRule(EcoRule):
    """R001: 假标准编号检测"""

    def __init__(self):
        super().__init__(
            id="R001",
            name="假标准编号",
            pattern=r"GB(\d{4,})",
            check=self._check_impl,
            correction=self._correct_impl,
            base_confidence=0.95,
        )

    def _check_impl(self, text: str, match: Optional[re.Match]) -> bool:
        if match:
            number_str = match.group(1)
            try:
                number = int(number_str)
                return number > 9999
            except ValueError:
                return False
        return False

    def _correct_impl(self, match: Optional[re.Match], text: str) -> str:
        return text.replace(match.group(0), "[标准编号]") if match else text


class TimeTravelRule(EcoRule):
    """R003: 时间穿越检测"""

    def __init__(self):
        super().__init__(
            id="R003",
            name="时间穿越",
            pattern=r"(\d{4})年",
            check=self._check_impl,
            correction=self._correct_impl,
            base_confidence=0.90,
        )

    def _check_impl(self, text: str, match: Optional[re.Match]) -> bool:
        if match:
            year = int(match.group(1))
            current_year = datetime.now().year
            return year > current_year
        return False

    def _correct_impl(self, match: Optional[re.Match], text: str) -> str:
        return text


class SelfContradictionRule(EcoRule):
    """R004: 自相矛盾检测"""

    CONTRADICTION_PAIRS = [
        ("有毒", "无害"),
        ("正确", "错误"),
        ("是", "不是"),
        ("有", "没有"),
        ("可以", "不可以"),
        ("必须", "不必"),
    ]

    def __init__(self):
        super().__init__(
            id="R004",
            name="自相矛盾",
            pattern=r".+",
            check=self._check_impl,
            correction=self._correct_impl,
            base_confidence=0.92,
        )

    def _check_impl(self, text: str, match: Optional[re.Match]) -> bool:
        for pos, neg in self.CONTRADICTION_PAIRS:
            if pos in text and neg in text:
                return True
        return False

    def _correct_impl(self, match: Optional[re.Match], text: str) -> str:
        return text


class WrongLegalStatusRule(EcoRule):
    """R005: 错误法律状态检测"""

    def __init__(self):
        super().__init__(
            id="R005",
            name="错误法律状态",
            pattern=r"(.*?(?:法|法规|条例))(未颁布|未实施)",
            check=self._check_impl,
            correction=self._correct_impl,
            base_confidence=0.95,
        )

    def _check_impl(self, text: str, match: Optional[re.Match]) -> bool:
        if match:
            return "未颁布" in match.group(0) or "未实施" in match.group(0)
        return False

    def _correct_impl(self, match: Optional[re.Match], text: str) -> str:
        return text.replace("未颁布", "已颁布").replace("未实施", "已实施")


class FakeHistoryRule(EcoRule):
    """R006: 虚假历史检测"""

    KNOWN_LAWS = {
        "环境保护法": 1989,
        "大气污染防治法": 1987,
        "水污染防治法": 1984,
    }

    def __init__(self):
        super().__init__(
            id="R006",
            name="虚假历史",
            pattern=r"(.*?)(202[5-9]|203\d)年(发布|实施|颁布)",
            check=self._check_impl,
            correction=self._correct_impl,
            base_confidence=0.90,
        )

    def _check_impl(self, text: str, match: Optional[re.Match]) -> bool:
        if match and "2025" in match.group(0):
            for law, year in self.KNOWN_LAWS.items():
                if law in text:
                    return True
        return False

    def _correct_impl(self, match: Optional[re.Match], text: str) -> str:
        return text


def get_all_rules() -> list[EcoRule]:
    """获取所有生态规则"""
    return [
        FakeStandardRule(),
        TimeTravelRule(),
        SelfContradictionRule(),
        WrongLegalStatusRule(),
        FakeHistoryRule(),
    ]
