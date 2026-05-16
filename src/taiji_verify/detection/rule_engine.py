"""
Rule Engine - 规则引擎

对应 WFGYVerifier.ts 的 Python 实现

功能:
- 规则匹配: 正则pattern或函数
- 权重归一化: 总和为1
- 符号一致性 = passedWeight/totalWeight
- 知识库匹配+来源追溯
- minimumScore默认0.7

接口: add_rule / remove_rule / add_knowledge_entry / verify / verify_symbols / extract_symbols / get_rules
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional
import jieba


@dataclass
class Rule:
    """验证规则"""

    id: str
    pattern: str
    check: Callable[[str, re.Match], bool]
    correction: Callable[[re.Match, str], str] | None = None
    base_confidence: float = 1.0
    weight: float = 1.0


@dataclass
class VerificationRule:
    """匹配到的验证规则"""

    rule: Rule
    match: re.Match | None
    passed: bool
    confidence: float
    correction_applied: bool = False
    corrected_text: Optional[str] = None


@dataclass
class KnowledgeMatch:
    """知识匹配结果"""

    entry_id: str
    coverage: float
    similarity: float
    matched_keywords: list[str]


@dataclass
class VerificationResult:
    """验证结果"""

    passed: bool
    confidence: float
    matched_rules: list[VerificationRule]
    knowledge_matches: list[KnowledgeMatch] = field(default_factory=list)
    corrected_text: Optional[str] = None
    symbol_consistency: Optional[float] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class SymbolConsistencyResult:
    """符号一致性结果"""

    passed_weight: int
    total_weight: int
    symbol_consistency: float
    matched_symbols: list[str] = field(default_factory=list)


@dataclass
class KnowledgeEntry:
    """知识库条目"""

    entry_id: str
    content: str
    keywords: list[str]
    source: str = ""
    metadata: dict = field(default_factory=dict)


class RuleEngine:
    """
    规则引擎

    Usage::
        engine = RuleEngine()
        engine.add_rule(Rule(
            id="R001",
            pattern=r"GB\\d{4,}",
            check=lambda text, match: int(match.group(0)[2:]) > 9999,
            correction=lambda match, text: text.replace(match.group(0), "[标准编号]"),
            base_confidence=0.95
        ))
        result = engine.verify("符合GB12345标准")
        print(result.passed, result.confidence)
    """

    def __init__(self, minimum_score: float = 0.7):
        self.minimum_score = minimum_score
        self._rules: dict[str, Rule] = {}
        self._knowledge_base: dict[str, KnowledgeEntry] = {}
        self._inverted_index: dict[str, set[str]] = {}

    def add_rule(self, rule: Rule) -> None:
        """添加规则"""
        self._rules[rule.id] = rule

    def remove_rule(self, rule_id: str) -> bool:
        """移除规则"""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    def get_rules(self) -> list[Rule]:
        """获取所有规则"""
        return list(self._rules.values())

    def add_knowledge_entry(
        self,
        entry_id: str,
        content: str,
        keywords: list[str],
        source: str = "",
        metadata: Optional[dict] = None,
    ) -> None:
        """添加知识库条目"""
        entry = KnowledgeEntry(
            entry_id=entry_id,
            content=content,
            keywords=keywords,
            source=source,
            metadata=metadata or {},
        )
        self._knowledge_base[entry_id] = entry

        for keyword in keywords:
            if keyword not in self._inverted_index:
                self._inverted_index[keyword] = set()
            self._inverted_index[keyword].add(entry_id)

    def verify(self, text: str) -> VerificationResult:
        """
        验证文本

        Args:
            text: 待验证文本

        Returns:
            VerificationResult 验证结果
        """
        matched_rules: list[VerificationRule] = []
        total_weight = 0.0
        passed_weight = 0.0
        corrected_text = text

        for rule in self._rules.values():
            pattern = re.compile(rule.pattern)
            match = pattern.search(text)

            if match:
                try:
                    passed = rule.check(text, match)
                except Exception:
                    passed = False

                confidence = rule.base_confidence if passed else rule.base_confidence * 0.5
                correction_applied = False
                rule_corrected = None

                if not passed and rule.correction:
                    rule_corrected = rule.correction(match, text)
                    correction_applied = True
                    if rule_corrected:
                        corrected_text = rule_corrected

                matched_rules.append(
                    VerificationRule(
                        rule=rule,
                        match=match,
                        passed=passed,
                        confidence=confidence,
                        correction_applied=correction_applied,
                        corrected_text=rule_corrected,
                    )
                )

                total_weight += rule.weight
                if passed:
                    passed_weight += rule.weight

        knowledge_matches = self._check_knowledge_base(text)

        if total_weight > 0:
            score = passed_weight / total_weight
        else:
            score = 1.0

        return VerificationResult(
            passed=score >= self.minimum_score,
            confidence=score,
            matched_rules=matched_rules,
            knowledge_matches=knowledge_matches,
            corrected_text=corrected_text if corrected_text != text else None,
            metadata={
                "total_weight": total_weight,
                "passed_weight": passed_weight,
            },
        )

    def verify_symbols(self, text: str) -> SymbolConsistencyResult:
        """
        验证符号一致性

        Args:
            text: 待验证文本

        Returns:
            SymbolConsistencyResult 符号一致性结果
        """
        matched_symbols: list[str] = []
        passed_weight = 0
        total_weight = 0

        for rule in self._rules.values():
            pattern = re.compile(rule.pattern)
            match = pattern.search(text)

            if match:
                matched_symbols.append(match.group(0))
                try:
                    passed = rule.check(text, match)
                except Exception:
                    passed = False

                total_weight += rule.weight
                if passed:
                    passed_weight += rule.weight

        if total_weight > 0:
            consistency = passed_weight / total_weight
        else:
            consistency = 1.0

        return SymbolConsistencyResult(
            passed_weight=passed_weight,
            total_weight=total_weight,
            symbol_consistency=consistency,
            matched_symbols=matched_symbols,
        )

    def extract_symbols(self, text: str) -> list[str]:
        """
        提取符号/实体

        Args:
            text: 待提取文本

        Returns:
            提取的符号列表
        """
        symbols: list[str] = []

        patterns = [
            (r"\d+(?:\.\d+)?%", "percentage"),
            (r"\d+(?:\.\d+)?", "number"),
            (r"[A-Z]{2,}[A-Z0-9]*", "abbreviation"),
            (r"GB[A-Z0-9]+", "standard"),
            (r"第[一二三四五六七八九十百千万\d]+[条章节款]", "clause"),
        ]

        for pattern, label in patterns:
            matches = re.findall(pattern, text)
            symbols.extend(matches)

        chinese_words = list(jieba.cut(text))
        symbols.extend([w for w in chinese_words if len(w) >= 2])

        return list(set(symbols))

    def _check_knowledge_base(self, text: str) -> list[KnowledgeMatch]:
        """
        检查知识库匹配

        Args:
            text: 待检查文本

        Returns:
            匹配的知识条目列表
        """
        matches: list[KnowledgeMatch] = []
        text_keywords = set(self.extract_symbols(text))

        for entry_id, entry in self._knowledge_base.items():
            entry_keywords = set(entry.keywords)
            intersection = text_keywords & entry_keywords

            if intersection:
                coverage = len(intersection) / len(entry_keywords) if entry_keywords else 0
                similarity = (
                    len(intersection) / len(text_keywords | entry_keywords)
                    if text_keywords and entry_keywords
                    else 0
                )

                matches.append(
                    KnowledgeMatch(
                        entry_id=entry_id,
                        coverage=coverage,
                        similarity=similarity,
                        matched_keywords=list(intersection),
                    )
                )

        matches.sort(key=lambda m: m.similarity, reverse=True)
        return matches[:10]

    def query_by_keyword(self, keyword: str) -> list[str]:
        """
        通过关键词查询知识库条目

        Args:
            keyword: 关键词

        Returns:
            匹配的条目ID列表
        """
        return list(self._inverted_index.get(keyword, set()))

    def clear_rules(self) -> None:
        """清除所有规则"""
        self._rules.clear()

    def clear_knowledge_base(self) -> None:
        """清除知识库"""
        self._knowledge_base.clear()
        self._inverted_index.clear()
