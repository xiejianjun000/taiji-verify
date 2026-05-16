"""
Twin Atlas - 双图

Forward Atlas(路由发现) + Bridge(耦合层) + Inverse Atlas(逆向治理)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ForwardResult:
    """正向路由结果"""
    target_domain: str
    route_path: list[str]
    confidence: float


@dataclass
class InverseResult:
    """逆向治理结果"""
    is_valid: bool
    validation_details: dict
    issues: list[str]


@dataclass
class AtlasResult:
    """双图结果"""
    forward_result: ForwardResult
    inverse_result: InverseResult
    coupled: bool


class TwinAtlas:
    """
    双图

    Usage::
        atlas = TwinAtlas()
        result = atlas.execute("碳排放权交易分析")
        print(result.coupled)
    """

    def __init__(self):
        self._domain_map = {
            "碳排放": "环境保护",
            "法律": "法规",
            "经济": "财政",
        }

    def forward_route(self, input_text: str) -> ForwardResult:
        """正向路由"""
        target_domain = "通用"
        route_path = ["input"]

        for keyword, domain in self._domain_map.items():
            if keyword in input_text:
                target_domain = domain
                route_path.append(keyword)
                route_path.append(domain)

        return ForwardResult(
            target_domain=target_domain,
            route_path=route_path,
            confidence=0.9 if len(route_path) > 1 else 0.5,
        )

    def inverse_validate(self, input_text: str) -> InverseResult:
        """逆向验证"""
        issues = []

        if len(input_text) < 5:
            issues.append("输入过短")

        if "错误" in input_text and "正确" in input_text:
            issues.append("存在矛盾")

        return InverseResult(
            is_valid=len(issues) == 0,
            validation_details={"length": len(input_text)},
            issues=issues,
        )

    def execute(self, input_text: str) -> AtlasResult:
        """执行双图"""
        forward = self.forward_route(input_text)
        inverse = self.inverse_validate(input_text)

        coupled = forward.confidence > 0.5 and inverse.is_valid

        return AtlasResult(
            forward_result=forward,
            inverse_result=inverse,
            coupled=coupled,
        )
