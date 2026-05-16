"""
Twin Atlas - 双图

扩展领域映射：
- 碳排放/环境
- 法律/法规
- 经济/财政
- 技术/工程
- 医疗/健康
- 教育/培训
- 金融/投资
- 能源/电力
- 交通/物流
- 农业/农村
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
    domain_keywords: list[str]


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
    双图 - 扩展领域映射

    Usage::
        atlas = TwinAtlas()
        result = atlas.execute("碳排放权交易分析")
        print(result.coupled)
    """

    DOMAIN_MAP = {
        "碳排放": {"domain": "环境保护", "keywords": ["碳", "排放", "环保", "污染"]},
        "环境": {"domain": "环境保护", "keywords": ["环境", "生态", "绿色"]},
        "法律": {"domain": "法规", "keywords": ["法", "法规", "条例", "规定"]},
        "法规": {"domain": "法规", "keywords": ["法规", "法律", "章"]},
        "经济": {"domain": "经济财政", "keywords": ["经济", "GDP", "增长"]},
        "财政": {"domain": "经济财政", "keywords": ["财政", "税收", "预算"]},
        "技术": {"domain": "技术工程", "keywords": ["技术", "工程", "系统"]},
        "工程": {"domain": "技术工程", "keywords": ["工程", "建设", "施工"]},
        "医疗": {"domain": "医疗健康", "keywords": ["医疗", "医院", "健康"]},
        "健康": {"domain": "医疗健康", "keywords": ["健康", "疾病", "治疗"]},
        "教育": {"domain": "教育培训", "keywords": ["教育", "学校", "培训"]},
        "培训": {"domain": "教育培训", "keywords": ["培训", "学习", "课程"]},
        "金融": {"domain": "金融投资", "keywords": ["金融", "银行", "投资"]},
        "投资": {"domain": "金融投资", "keywords": ["投资", "理财", "基金"]},
        "能源": {"domain": "能源电力", "keywords": ["能源", "电力", "电网"]},
        "电力": {"domain": "能源电力", "keywords": ["电力", "供电", "用电"]},
        "交通": {"domain": "交通物流", "keywords": ["交通", "物流", "运输"]},
        "物流": {"domain": "交通物流", "keywords": ["物流", "仓储", "配送"]},
        "农业": {"domain": "农业农村", "keywords": ["农业", "农村", "粮食"]},
        "农村": {"domain": "农业农村", "keywords": ["农村", "农民", "土地"]},
        "安全": {"domain": "安全生产", "keywords": ["安全", "生产", "事故"]},
        "生产": {"domain": "安全生产", "keywords": ["生产", "制造", "工厂"]},
        "数据": {"domain": "数据信息", "keywords": ["数据", "信息", "系统"]},
        "信息": {"domain": "数据信息", "keywords": ["信息", "网络", "系统"]},
        "文化": {"domain": "文化传媒", "keywords": ["文化", "传媒", "宣传"]},
        "传媒": {"domain": "文化传媒", "keywords": ["传媒", "媒体", "出版"]},
        "旅游": {"domain": "旅游服务", "keywords": ["旅游", "酒店", "服务"]},
        "服务": {"domain": "旅游服务", "keywords": ["服务", "客服", "体验"]},
        "房地产": {"domain": "房地产", "keywords": ["房产", "地产", "建筑"]},
        "建筑": {"domain": "房地产", "keywords": ["建筑", "施工", "设计"]},
    }

    def __init__(self):
        self._domain_map = self.DOMAIN_MAP

    def forward_route(self, input_text: str) -> ForwardResult:
        """正向路由"""
        target_domains = []
        matched_keywords = []

        for keyword, mapping in self._domain_map.items():
            if keyword in input_text:
                target_domains.append(mapping["domain"])
                matched_keywords.append(keyword)

        target_domains = list(set(target_domains))

        if not target_domains:
            target_domain = "通用"
        elif len(target_domains) == 1:
            target_domain = target_domains[0]
        else:
            target_domain = "; ".join(target_domains)

        route_path = ["input"] + matched_keywords + [target_domain]
        confidence = min(0.9, 0.5 + len(matched_keywords) * 0.1)

        return ForwardResult(
            target_domain=target_domain,
            route_path=route_path,
            confidence=confidence,
            domain_keywords=matched_keywords,
        )

    def inverse_validate(self, input_text: str) -> InverseResult:
        """逆向验证"""
        issues = []

        if len(input_text) < 5:
            issues.append("输入过短")

        if "错误" in input_text and "正确" in input_text:
            issues.append("存在矛盾")

        forward = self.forward_route(input_text)
        if forward.confidence < 0.5 and len(forward.domain_keywords) == 0:
            issues.append("无法确定领域")

        return InverseResult(
            is_valid=len(issues) == 0,
            validation_details={
                "length": len(input_text),
                "domains": forward.domain_keywords,
                "confidence": forward.confidence,
            },
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
