"""
中文领域知识库

扩展Taiji Verify对中国各垂直领域的知识支持：
- 医疗健康
- 法律法规
- 金融财经
- 教育考试
- 食品安全
- 环境保护
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class KnowledgeEntry:
    """知识条目"""
    id: str
    content: str
    category: str
    source: str
    keywords: list[str] = field(default_factory=list)
    verified: bool = True


class ChineseKnowledgeBase:
    """
    中文领域知识库

    Usage:
        kb = ChineseKnowledgeBase()
        kb.load_medical()
        kb.load_legal()
        kb.load_financial()

        # 查询
        results = kb.query("糖尿病", category="medical")
    """

    def __init__(self):
        self._entries: dict[str, list[KnowledgeEntry]] = {
            "medical": [],
            "legal": [],
            "financial": [],
            "education": [],
            "food_safety": [],
            "environmental": [],
        }

    def load_medical(self) -> ChineseKnowledgeBase:
        """加载医疗健康知识"""
        self._entries["medical"] = [
            KnowledgeEntry(
                id="MED001",
                content="糖尿病是一组以高血糖为特征的代谢性疾病",
                category="medical",
                source="中华医学会糖尿病学分会",
                keywords=["糖尿病", "高血糖", "代谢", "胰岛素"],
            ),
            KnowledgeEntry(
                id="MED002",
                content="高血压是指以体循环动脉血压增高为主要特征，可伴有心、脑、肾等器官的功能或器质性损害的临床综合征",
                category="medical",
                source="中国高血压防治指南",
                keywords=["高血压", "血压", "心脑血管"],
            ),
            KnowledgeEntry(
                id="MED003",
                content="冠心病是冠状动脉粥样硬化性心脏病的简称，是由于冠状动脉发生粥样硬化导致管腔狭窄或闭塞，引起心肌缺血、缺氧或坏死",
                category="medical",
                source="中华心血管病杂志",
                keywords=["冠心病", "冠状动脉", "心肌缺血", "心绞痛"],
            ),
            KnowledgeEntry(
                id="MED004",
                content="恶性肿瘤是一类细胞不正常增殖的疾病，可侵入周围组织并通过血液或淋巴系统转移",
                category="medical",
                source="WHO肿瘤分类",
                keywords=["肿瘤", "癌症", "恶性肿瘤", "转移"],
            ),
            KnowledgeEntry(
                id="MED005",
                content="抑郁症是一种常见的精神障碍，以持续的情绪低落、兴趣减退为主要特征",
                category="medical",
                source="DSM-5/ICD-11",
                keywords=["抑郁症", "精神障碍", "情绪低落"],
            ),
            KnowledgeEntry(
                id="MED006",
                content="水是人由氢元素和氧元素组成的无机物，化学式为H2O",
                category="medical",
                source="化学教科书",
                keywords=["水", "H2O", "氢", "氧"],
            ),
            KnowledgeEntry(
                id="MED007",
                content="维生素C是一种水溶性维生素，人体缺乏会导致坏血病",
                category="medical",
                source="营养学教科书",
                keywords=["维生素C", "坏血病", "水溶性维生素"],
            ),
            KnowledgeEntry(
                id="MED008",
                content="流感是由流感病毒引起的急性呼吸道传染病",
                category="medical",
                source="传染病学",
                keywords=["流感", "流感病毒", "呼吸道"],
            ),
            KnowledgeEntry(
                id="MED009",
                content="COVID-19是由SARS-CoV-2病毒引起的传染病",
                category="medical",
                source="WHO",
                keywords=["新冠", "COVID", "SARS-CoV-2", "肺炎"],
            ),
            KnowledgeEntry(
                id="MED010",
                content="阿司匹林是一种非甾体抗炎药，用于解热、镇痛、抗炎",
                category="medical",
                source="药理学",
                keywords=["阿司匹林", "NSAIDs", "非甾体"],
            ),
        ]
        return self

    def load_legal(self) -> ChineseKnowledgeBase:
        """加载法律法规知识"""
        self._entries["legal"] = [
            KnowledgeEntry(
                id="LAW001",
                content="《中华人民共和国宪法》是中华人民共和国的根本大法",
                category="legal",
                source="全国人民代表大会",
                keywords=["宪法", "根本大法", "中华人民共和国"],
            ),
            KnowledgeEntry(
                id="LAW002",
                content="《中华人民共和国民法典》于2021年1月1日起施行",
                category="legal",
                source="全国人民代表大会",
                keywords=["民法典", "民法", "2021年"],
            ),
            KnowledgeEntry(
                id="LAW003",
                content="《中华人民共和国劳动法》保护劳动者合法权益",
                category="legal",
                source="全国人民代表大会",
                keywords=["劳动法", "劳动者", "权益"],
            ),
            KnowledgeEntry(
                id="LAW004",
                content="《中华人民共和国刑法》是规定犯罪和刑罚的法律",
                category="legal",
                source="全国人民代表大会",
                keywords=["刑法", "犯罪", "刑罚"],
            ),
            KnowledgeEntry(
                id="LAW005",
                content="《中华人民共和国公司法》规定公司的设立、组织机构和公司行为",
                category="legal",
                source="全国人民代表大会",
                keywords=["公司法", "公司", "企业"],
            ),
            KnowledgeEntry(
                id="LAW006",
                content="《中华人民共和国环境保护法》保护和改善环境，防治污染",
                category="legal",
                source="全国人民代表大会",
                keywords=["环境保护法", "污染", "环境"],
            ),
            KnowledgeEntry(
                id="LAW007",
                content="《中华人民共和国个人信息保护法》保护个人信息权益",
                category="legal",
                source="全国人民代表大会",
                keywords=["个人信息保护法", "隐私", "数据保护"],
            ),
            KnowledgeEntry(
                id="LAW008",
                content="《中华人民共和国劳动合同法》规范劳动合同的订立、履行、变更、解除和终止",
                category="legal",
                source="全国人民代表大会",
                keywords=["劳动合同法", "劳动合同", "劳动争议"],
            ),
            KnowledgeEntry(
                id="LAW009",
                content="《中华人民共和国食品安全法》保证食品安全，保障公众身体健康和生命安全",
                category="legal",
                source="全国人民代表大会",
                keywords=["食品安全法", "食品", "安全"],
            ),
            KnowledgeEntry(
                id="LAW010",
                content="《中华人民共和国著作权法》保护文学、艺术和科学作品作者的著作权",
                category="legal",
                source="全国人民代表大会",
                keywords=["著作权法", "版权", "知识产权"],
            ),
        ]
        return self

    def load_financial(self) -> ChineseKnowledgeBase:
        """加载金融财经知识"""
        self._entries["financial"] = [
            KnowledgeEntry(
                id="FIN001",
                content="GDP是国内生产总值的英文缩写，是衡量一国经济规模的重要指标",
                category="financial",
                source="国家统计局",
                keywords=["GDP", "国内生产总值", "经济规模"],
            ),
            KnowledgeEntry(
                id="FIN002",
                content="CPI是居民消费价格指数，用于反映通货膨胀水平",
                category="financial",
                source="国家统计局",
                keywords=["CPI", "通货膨胀", "物价指数"],
            ),
            KnowledgeEntry(
                id="FIN003",
                content="A股是指在中国境内上市的股票，以人民币计价",
                category="financial",
                source="中国证监会",
                keywords=["A股", "股票", "上证", "深证"],
            ),
            KnowledgeEntry(
                id="FIN004",
                content="美联储是美国的中央银行",
                category="financial",
                source="经济学常识",
                keywords=["美联储", "FED", "中央银行", "美元"],
            ),
            KnowledgeEntry(
                id="FIN005",
                content="比特币是一种基于区块链技术的去中心化数字货币",
                category="financial",
                source="经济学常识",
                keywords=["比特币", "BTC", "区块链", "加密货币"],
            ),
            KnowledgeEntry(
                id="FIN006",
                content="沪指是上海证券交易所综合股价指数",
                category="financial",
                source="上证所",
                keywords=["沪指", "上证指数", "SHCOMP"],
            ),
            KnowledgeEntry(
                id="FIN007",
                content="年化收益率是将投资回报转换为年度回报的计算方式",
                category="financial",
                source="金融学",
                keywords=["年化收益率", "投资回报", "收益"],
            ),
            KnowledgeEntry(
                id="FIN008",
                content="存款准备金率是商业银行必须存放在中央银行的存款比例",
                category="financial",
                source="中国人民银行",
                keywords=["存款准备金率", "央行", "货币政策"],
            ),
        ]
        return self

    def load_education(self) -> ChineseKnowledgeBase:
        """加载教育考试知识"""
        self._entries["education"] = [
            KnowledgeEntry(
                id="EDU001",
                content="中华人民共和国义务教育法规定国家对适龄儿童、少年实施九年义务教育",
                category="education",
                source="教育部",
                keywords=["义务教育", "九年义务教育", "免学费"],
            ),
            KnowledgeEntry(
                id="EDU002",
                content="高考是中国大陆普通高等学校招生全国统一考试",
                category="education",
                source="教育部",
                keywords=["高考", "全国统一考试", "招生"],
            ),
            KnowledgeEntry(
                id="EDU003",
                content="硕士学位研究生需在校学习2-3年",
                category="education",
                source="教育部",
                keywords=["硕士", "研究生", "学位"],
            ),
            KnowledgeEntry(
                id="EDU004",
                content="博士学位研究生学习年限一般为3-5年",
                category="education",
                source="教育部",
                keywords=["博士", "PhD", "研究生"],
            ),
            KnowledgeEntry(
                id="EDU005",
                content="普通话水平测试分为三级六等",
                category="education",
                source="教育部语言文字司",
                keywords=["普通话", "PSC", "等级"],
            ),
        ]
        return self

    def query(
        self,
        text: str,
        category: Optional[str] = None,
        limit: int = 5,
    ) -> list[KnowledgeEntry]:
        """
        查询相关知识条目

        Args:
            text: 查询文本
            category: 指定类别，不指定则搜索所有类别
            limit: 返回数量限制

        Returns:
            相关知识条目列表
        """
        text_lower = text.lower()
        results: list[tuple[int, KnowledgeEntry]] = []

        categories = [category] if category else self._entries.keys()

        for cat in categories:
            for entry in self._entries.get(cat, []):
                score = 0
                for keyword in entry.keywords:
                    if keyword.lower() in text_lower:
                        score += 1
                if score > 0:
                    results.append((score, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    def verify_fact(self, text: str) -> tuple[bool, Optional[str]]:
        """
        验证事实

        Args:
            text: 待验证文本

        Returns:
            (是否已知为真, 相关信息)
        """
        results = self.query(text, limit=1)
        if results:
            entry = results[0]
            for keyword in entry.keywords:
                if keyword in text:
                    return True, f"来源: {entry.source}"
        return False, None

    def get_categories(self) -> list[str]:
        """获取所有类别"""
        return list(self._entries.keys())

    def entry_count(self, category: Optional[str] = None) -> int:
        """获取条目数量"""
        if category:
            return len(self._entries.get(category, []))
        return sum(len(entries) for entries in self._entries.values())


def create_default_knowledge_base() -> ChineseKnowledgeBase:
    """创建默认知识库（包含所有领域）"""
    kb = ChineseKnowledgeBase()
    kb.load_medical()
    kb.load_legal()
    kb.load_financial()
    kb.load_education()
    return kb
