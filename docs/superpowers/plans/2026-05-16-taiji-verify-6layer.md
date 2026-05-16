# Taiji Verify 六层架构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** 构建完整的 Taiji Verify 六层验证引擎，实现从核心层(Layer 1)到执行层(Layer 6)的全栈验证能力

**Architecture:** 六层模块化架构，Layer 1 已完成，从 Layer 2 开始构建检测层、推理层、诊断层、治理层、执行层，最终融合到主引擎

**Tech Stack:** Python 3.9+, NumPy, pytest, TDD

---

## 目录结构

```
taiji-verify/
├── src/taiji_verify/
│   ├── core/                     ✅已完成 (原有文件)
│   ├── detection/                ← Layer 2 检测层
│   │   ├── __init__.py
│   │   ├── rule_engine.py        规则引擎
│   │   ├── consistency.py        自一致性检查
│   │   ├── source_tracer.py      知识溯源
│   │   ├── hallucination_detector.py  综合幻觉检测
│   │   ├── stream_guard.py       流式守卫
│   │   └── eco_rules.py          生态环境规则R001-R006
│   ├── reasoning/                 ← Layer 3 推理层
│   │   ├── __init__.py
│   │   ├── seven_step_chain.py   七步推理链
│   │   ├── checkpoint.py         记忆检查点
│   │   ├── coupler.py            耦合器
│   │   └── semantic_firewall.py  语义防火墙
│   ├── diagnosis/                 ← Layer 4 诊断层
│   │   ├── __init__.py
│   │   ├── symptom_map.py        病候图（从core迁移）
│   │   ├── failure_modes.py      失败检测器（从core迁移）
│   │   ├── global_fix_map.py      全局修复图
│   │   └── troubleshooting_atlas.py  故障排除地图
│   ├── governance/               ← Layer 5 治理层
│   │   ├── __init__.py
│   │   ├── twin_atlas.py         双图
│   │   ├── inverse_atlas.py      逆图
│   │   └── governance_gates.py  7治理门
│   ├── execution/                 ← Layer 6 执行层
│   │   ├── __init__.py
│   │   ├── goal_compiler.py      目标编译器
│   │   ├── task_atoms.py         任务原子化
│   │   ├── execution_token.py    执行令牌板
│   │   └── leak_auditor.py       泄漏审计
│   ├── engine.py                 主引擎（重写，融合6层）
│   └── __init__.py
├── tests/                        每模块1个测试文件
├── data/fix_map_entries.json     Global Fix Map数据
└── docs/
```

---

## Task 1: Layer 2 Detection层 - 规则引擎

### 文件
- Create: `src/taiji_verify/detection/__init__.py`
- Create: `src/taiji_verify/detection/rule_engine.py`
- Create: `tests/test_detection/test_rule_engine.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_detection/test_rule_engine.py
import pytest
from taiji_verify.detection.rule_engine import (
    Rule, RuleEngine, VerificationRule, SymbolConsistencyResult
)

class TestRuleEngine:
    def test_add_and_verify_rule(self):
        engine = RuleEngine()
        rule = Rule(
            id="R001",
            pattern=r"GB\d{4,}",
            check=lambda text, match: int(match.group(0)[2:]) > 9999,
            correction=lambda match, text: text.replace(match.group(0), "[标准编号]"),
            base_confidence=0.95
        )
        engine.add_rule(rule)
        result = engine.verify("符合GB12345标准")
        assert result.passed is False
        assert result.confidence == 0.95

    def test_symbol_consistency(self):
        engine = RuleEngine()
        engine.add_rule(Rule(id="S1", pattern="是", check=lambda t, m: True))
        engine.add_rule(Rule(id="S2", pattern="不是", check=lambda t, m: False))
        engine.add_rule(Rule(id="S3", pattern="对", check=lambda t, m: True))
        result = engine.verify_symbols("这是对的")
        assert result.symbol_consistency == pytest.approx(2/3, rel=0.01)
        assert result.passed_weight == 2
        assert result.total_weight == 3

    def test_knowledge_base_match(self):
        engine = RuleEngine()
        engine.add_knowledge_entry(
            entry_id="KB001",
            content="环境保护法是中国环境保护的基本法律",
            keywords=["环境保护法", "基本法律"]
        )
        result = engine.verify("环境保护法规定了污染治理要求")
        assert result.knowledge_matches[0].entry_id == "KB001"
        assert result.knowledge_matches[0].coverage > 0.5

    def test_extract_symbols(self):
        engine = RuleEngine()
        symbols = engine.extract_symbols("碳排放量增加了15%，同比增长20%")
        assert "碳排放量" in symbols
        assert "增加" in symbols

    def test_minimum_score_threshold(self):
        engine = RuleEngine(minimum_score=0.9)
        engine.add_rule(Rule(
            id="W1", pattern="正确", weight=0.5,
            check=lambda t, m: True, correction=lambda m, t: t, base_confidence=1.0
        ))
        engine.add_rule(Rule(
            id="W2", pattern="错误", weight=0.5,
            check=lambda t, m: False, correction=lambda m, t: t, base_confidence=1.0
        ))
        result = engine.verify("包含正确和错误的内容")
        assert result.passed is True
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_detection/test_rule_engine.py -v
```

Expected: FAIL - ModuleNotFoundError

- [ ] **Step 3: 实现最小代码通过测试**

实现 `rule_engine.py` 包含:
- `Rule` 数据类: id, pattern, weight, check, correction, base_confidence
- `VerificationRule` 数据类: rule, match, passed, confidence, correction
- `SymbolConsistencyResult`: passed_weight, total_weight, symbol_consistency
- `RuleEngine` 类:
  - `__init__(minimum_score=0.7)`
  - `add_rule(rule)`, `remove_rule(rule_id)`, `get_rules()`
  - `verify(text)` → VerificationResult
  - `verify_symbols(text)` → SymbolConsistencyResult
  - `extract_symbols(text)` → List[str]
  - `add_knowledge_entry(entry_id, content, keywords)`

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_detection/test_rule_engine.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/detection/rule_engine.py tests/test_detection/test_rule_engine.py
git commit -m "feat(detection): add rule engine with symbol consistency"
```

---

## Task 2: Layer 2 Detection层 - 自一致性检查

### 文件
- Create: `src/taiji_verify/detection/consistency.py`
- Create: `tests/test_detection/test_consistency.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_detection/test_consistency.py
import pytest
from taiji_verify.detection.consistency import (
    SelfConsistencyChecker, SimilarityResult, SamplingConfig
)

class TestSelfConsistencyChecker:
    def test_jaccard_similarity(self):
        checker = SelfConsistencyChecker()
        set1 = {"环境", "保护", "法"}
        set2 = {"环境", "法", "规"}
        sim = checker.jaccard_similarity(set1, set2)
        assert sim == pytest.approx(2/3, rel=0.01)

    def test_levenshtein_similarity(self):
        checker = SelfConsistencyChecker()
        sim = checker.levenshtein_similarity("环境保护", "环境保护法")
        assert sim > 0.5

    def test_cosine_similarity(self):
        checker = SelfConsistencyChecker()
        vec1 = [1, 0, 1]
        vec2 = [1, 1, 1]
        sim = checker.cosine_similarity(vec1, vec2)
        assert sim == pytest.approx(2/3, rel=0.01)

    def test_check_self_consistency(self):
        checker = SelfConsistencyChecker(default_samples=3)
        def sampler():
            return "环境保护法是中国环境保护的基本法律"
        result = checker.check_self_consistency(sampler)
        assert result.passed is True
        assert result.avg_similarity > 0.7
        assert len(result.samples) == 3

    def test_batch_consistency(self):
        checker = SelfConsistencyChecker()
        texts = ["环境保护法", "环境保护法律", "环境保护法规"]
        result = checker.batch_consistency(texts)
        assert result.avg_similarity > 0.5
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_detection/test_consistency.py -v
```

- [ ] **Step 3: 实现最小代码**

实现 `consistency.py`:
- `SimilarityResult`: similarity, method, samples
- `SelfConsistencyChecker`:
  - `jaccard_similarity(set1, set2)` - 集合Jaccard
  - `levenshtein_similarity(s1, s2)` - Levenshtein距离转相似度
  - `cosine_similarity(vec1, vec2)` - 余弦相似度
  - `check_self_consistency(sampler_fn, samples=3)` - 自一致性检查
  - `batch_consistency(texts)` - 批量文本一致性
  - 默认阈值 0.7

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_detection/test_consistency.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/detection/consistency.py tests/test_detection/test_consistency.py
git commit -m "feat(detection): add self-consistency checker with 3 similarity methods"
```

---

## Task 3: Layer 2 Detection层 - 知识溯源与幻觉检测

### 文件
- Create: `src/taiji_verify/detection/source_tracer.py`
- Create: `src/taiji_verify/detection/hallucination_detector.py`
- Create: `tests/test_detection/test_source_tracer.py`
- Create: `tests/test_detection/test_hallucination_detector.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_detection/test_source_tracer.py
import pytest
from taiji_verify.detection.source_tracer import SourceTracer, TraceResult

class TestSourceTracer:
    def test_add_and_query_entry(self):
        tracer = SourceTracer()
        tracer.add_entry(
            entry_id="E001",
            content="环境保护法于2022年修订",
            keywords=["环境保护法", "修订", "2022"]
        )
        result = tracer.query("环境保护法何时修订")
        assert result.matched_entry_ids == ["E001"]
        assert result.coverage > 0.5

    def test_inverted_index(self):
        tracer = SourceTracer()
        tracer.add_entry("E1", "碳排放权交易管理办法", ["碳排放", "交易"])
        tracer.add_entry("E2", "碳达峰实施方案", ["碳达峰", "实施"])
        results = tracer.query_by_keyword("碳排放")
        assert len(results) == 2

    def test_batch_trace(self):
        tracer = SourceTracer()
        tracer.add_entry("E1", "环境质量标准规定", ["环境质量", "标准"])
        texts = [
            "环境质量标准需要严格执行",
            "经济发展与环境保护平衡"
        ]
        results = tracer.batch_trace(texts)
        assert len(results) == 2

# tests/test_detection/test_hallucination_detector.py
import pytest
from taiji_verify.detection.hallucination_detector import (
    HallucinationDetector, RiskLevel, DetectionResult
)

class TestHallucinationDetector:
    def test_detect_with_weighted_score(self):
        detector = HallucinationDetector()
        text = "根据GB12345标准，环境质量应符合规定要求"
        result = detector.detect(text)
        assert hasattr(result, 'weighted_score')
        assert hasattr(result, 'risk_level')
        assert isinstance(result.risk_level, RiskLevel)

    def test_risk_level_threshold(self):
        detector = HallucinationDetector(risk_threshold=0.8)
        detector.rule_weight = 0.4
        detector.consistency_weight = 0.3
        detector.trace_weight = 0.3
        result = detector.detect("测试文本内容")
        assert isinstance(result.risk_level, RiskLevel)

    def test_segmented_detection(self):
        detector = HallucinationDetector()
        text = "第一句内容。第二句内容。第三句内容。"
        result = detector.detect_segmented(text)
        assert len(result.segments) >= 3
        assert any(r.is_hallucination for r in result.segments)
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_detection/test_source_tracer.py tests/test_detection/test_hallucination_detector.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `source_tracer.py`:
- `TraceResult`: matched_entry_ids, coverage, similarity_scores, matched_keywords
- `SourceTracer`:
  - `add_entry(entry_id, content, keywords)`
  - `query(text)` → TraceResult
  - `query_by_keyword(keyword)` → List[entry_ids]
  - `batch_trace(texts)` → List[TraceResult]
  - 倒排索引实现，Jaccard内容相似度
  - 默认maxSources=10

实现 `hallucination_detector.py`:
- `RiskLevel`: LOW, MEDIUM, HIGH, CRITICAL
- `SegmentResult`: text, is_hallucination, confidence, matched_sources
- `DetectionResult`: weighted_score, risk_level, details, segments
- `HallucinationDetector`:
  - `__init__(rule_weight=0.4, consistency_weight=0.3, trace_weight=0.3)`
  - `detect(text)` → DetectionResult
  - `detect_segmented(text)` → DetectionResult
  - 风险评分 = weightedScore/totalWeight
  - 阈值 0.8

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_detection/test_source_tracer.py tests/test_detection/test_hallucination_detector.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/detection/source_tracer.py src/taiji_verify/detection/hallucination_detector.py
git add tests/test_detection/test_source_tracer.py tests/test_detection/test_hallucination_detector.py
git commit -m "feat(detection): add source tracer and hallucination detector"
```

---

## Task 4: Layer 2 Detection层 - 生态规则与流式守卫

### 文件
- Create: `src/taiji_verify/detection/eco_rules.py`
- Create: `src/taiji_verify/detection/stream_guard.py`
- Create: `tests/test_detection/test_eco_rules.py`
- Create: `tests/test_detection/test_stream_guard.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_detection/test_eco_rules.py
import pytest
from datetime import datetime
from taiji_verify.detection.eco_rules import (
    FakeStandardRule, TimeTravelRule, SelfContradictionRule,
    WrongLegalStatusRule, FakeHistoryRule, get_all_rules
)

class TestEcoRules:
    def test_fake_standard_rule(self):
        rule = FakeStandardRule()
        assert rule.check("GB999999标准规定", None) is True
        assert rule.check("GB1234标准", None) is False
        assert rule.correction(None, "GB999999有问题") == "GB999999有问题"

    def test_time_travel_rule(self):
        rule = TimeTravelRule()
        assert rule.check("该法律于2050年颁布", None) is True
        assert rule.check("该法律于2020年颁布", None) is False

    def test_self_contradiction_rule(self):
        rule = SelfContradictionRule()
        assert rule.check("该物质有毒但也无害", None) is True
        assert rule.check("该物质有毒", None) is False

    def test_wrong_legal_status_rule(self):
        rule = WrongLegalStatusRule()
        assert rule.check("环境保护法未颁布", None) is True
        assert rule.check("环境保护法已颁布", None) is False

    def test_fake_history_rule(self):
        rule = FakeHistoryRule()
        assert rule.check("该法规2025年发布", None) is True
        assert rule.check("该法规1990年发布", None) is False

    def test_get_all_rules(self):
        rules = get_all_rules()
        assert len(rules) == 5
        assert all(r.base_confidence >= 0.9 for r in rules)

# tests/test_detection/test_stream_guard.py
import pytest
from taiji_verify.detection.stream_guard import StreamGuard, GuardConfig

class TestStreamGuard:
    def test_stream_guard_initialization(self):
        guard = StreamGuard(token_threshold=100, check_interval=50)
        assert guard.token_threshold == 100
        assert guard.current_tokens == 0

    def test_add_tokens_and_check(self):
        guard = StreamGuard(token_threshold=10, check_interval=5)
        guard.add_tokens("今天天气")
        assert guard.current_tokens > 0
        guard.add_tokens("很好")
        if guard.current_tokens >= guard.token_threshold:
            result = guard.check_batch()
            assert result is not None

    def test_stream_guard_context(self):
        guard = StreamGuard(token_threshold=20)
        guard.set_context("碳排放权交易")
        assert "碳排放权交易" in guard.context
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_detection/test_eco_rules.py tests/test_detection/test_stream_guard.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `eco_rules.py`:
- 每个规则实现 `Rule` 接口
- `FakeStandardRule`: GB编号>9999检测
- `TimeTravelRule`: 年份>当前年检测
- `SelfContradictionRule`: 正反义同时出现
- `WrongLegalStatusRule`: 说"未颁布"
- `FakeHistoryRule`: 错误的2025年
- `get_all_rules()` 返回所有规则

实现 `stream_guard.py`:
- `GuardConfig`: token_threshold, check_interval
- `StreamGuard`:
  - `add_tokens(text)`
  - `check_batch()` → 检查结果
  - `set_context(text)`
  - 支持流式实时场景

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_detection/test_eco_rules.py tests/test_detection/test_stream_guard.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/detection/eco_rules.py src/taiji_verify/detection/stream_guard.py
git add tests/test_detection/test_eco_rules.py tests/test_detection/test_stream_guard.py
git commit -m "feat(detection): add eco rules R001-R006 and stream guard"
```

---

## Task 5: Layer 3 Reasoning层 - 七步推理链

### 文件
- Create: `src/taiji_verify/reasoning/__init__.py`
- Create: `src/taiji_verify/reasoning/seven_step_chain.py`
- Create: `tests/test_reasoning/test_seven_step_chain.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_reasoning/test_seven_step_chain.py
import pytest
from taiji_verify.reasoning.seven_step_chain import (
    SevenStepChain, StepInput, StepOutput, ChainConfig
)

class TestSevenStepChain:
    def test_chain_initialization(self):
        chain = SevenStepChain()
        assert chain.current_step == 0
        assert len(chain.steps) == 7

    def test_step1_parse(self):
        chain = SevenStepChain()
        input_data = StepInput(
            text="分析环境保护法的实施效果",
            goal="评估环境保护法的实施效果"
        )
        output = chain.execute_step(1, input_data)
        assert output.parsed_input is not None
        assert output.parsed_goal is not None

    def test_step2_compute_delta_s(self):
        chain = SevenStepChain()
        input_data = StepInput(text="输出文本", goal="标准答案")
        prev_output = StepOutput(parsed_input={"entities": []}, parsed_goal={"entities": []})
        output = chain.execute_step(2, input_data, prev_output)
        assert output.delta_s is not None
        assert output.gate_zone is not None

    def test_step3_memory_checkpoint(self):
        chain = SevenStepChain()
        output = chain.execute_step(3, StepInput(text=""), prev_output=StepOutput(
            delta_s=0.5, gate_zone="RISK"
        ))
        assert output.checkpoint_saved is True

    def test_full_chain_execution(self):
        chain = SevenStepChain()
        input_data = StepInput(
            text="碳排放权交易平台应当建立",
            goal="碳排放权交易平台应当建立完善的监管机制"
        )
        result = chain.execute_full_chain(input_data)
        assert result.final_output is not None
        assert result.steps_completed == 7
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_reasoning/test_seven_step_chain.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `seven_step_chain.py`:
- `StepInput`: text, goal, context, metadata
- `StepOutput`: step_name, result_data, delta_s, gate_zone, checkpoint_saved, correction_applied
- `ChainConfig`: max_retries, checkpoint_enabled, semantic_firewall_enabled
- `SevenStepChain`:
  - 7个步骤: Parse, Compute ΔS, Memory Checkpoint, 坤守·Residue, Coupler+乾进, 巽调·Rebalancer, 复归+Drunk
  - `execute_step(step_num, input_data, prev_output)`
  - `execute_full_chain(input_data)` → ChainResult

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_reasoning/test_seven_step_chain.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/reasoning/seven_step_chain.py tests/test_reasoning/test_seven_step_chain.py
git commit -m "feat(reasoning): add seven-step chain implementation"
```

---

## Task 6: Layer 3 Reasoning层 - 检查点与耦合器

### 文件
- Create: `src/taiji_verify/reasoning/checkpoint.py`
- Create: `src/taiji_verify/reasoning/coupler.py`
- Create: `src/taiji_verify/reasoning/semantic_firewall.py`
- Create: `tests/test_reasoning/test_checkpoint.py`
- Create: `tests/test_reasoning/test_coupler.py`
- Create: `tests/test_reasoning/test_semantic_firewall.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_reasoning/test_checkpoint.py
import pytest
from taiji_verify.reasoning.checkpoint import Checkpoint, CheckpointManager

class TestCheckpoint:
    def test_save_and_restore(self):
        manager = CheckpointManager()
        manager.save("step1", {"data": "value"}, delta_s=0.5)
        checkpoint = manager.restore("step1")
        assert checkpoint is not None
        assert checkpoint.data["data"] == "value"
        assert checkpoint.delta_s == 0.5

    def test_gate_check(self):
        manager = CheckpointManager()
        manager.save("safe", {"v": 1}, gate_zone="SAFE")
        manager.save("risk", {"v": 2}, gate_zone="RISK")
        assert manager.gate_check("safe", "RISK") is True
        assert manager.gate_check("risk", "SAFE") is False

    def test_checkpoint_list(self):
        manager = CheckpointManager()
        manager.save("cp1", {}, delta_s=0.1)
        manager.save("cp2", {}, delta_s=0.2)
        checkpoints = manager.list_checkpoints()
        assert len(checkpoints) == 2

# tests/test_reasoning/test_coupler.py
import pytest
from taiji_verify.reasoning.coupler import Coupler, ContractViolation

class TestCoupler:
    def test_coupler_delta_s_decrease_only(self):
        coupler = Coupler()
        assert coupler.check_progression(0.8, 0.5) is True
        assert coupler.check_progression(0.5, 0.8) is False

    def test_contract_enforcement(self):
        coupler = Coupler()
        with pytest.raises(ContractViolation):
            coupler.enforce_contract(
                current_delta=0.5,
                next_delta=0.8,
                local_force=1.0,
                global_tension=0.5
            )

# tests/test_reasoning/test_semantic_firewall.py
import pytest
from taiji_verify.reasoning.semantic_firewall import SemanticFirewall, FirewallResult

class TestSemanticFirewall:
    def test_firewall_pass(self):
        firewall = SemanticFirewall()
        result = firewall.check("正确的环境保护法分析")
        assert result.decision in ["PASS", "MODIFIED"]

    def test_firewall_block(self):
        firewall = SemanticFirewall()
        result = firewall.check("包含幻觉的虚假内容")
        assert result.decision in ["BLOCK", "ESCALATE"]

    def test_firewall_pipeline(self):
        firewall = SemanticFirewall()
        result = firewall.check_with_pipeline("测试文本")
        assert result.delta_s is not None
        assert len(result.step_results) > 0
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_reasoning/test_checkpoint.py tests/test_reasoning/test_coupler.py tests/test_reasoning/test_semantic_firewall.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `checkpoint.py`:
- `Checkpoint`: id, step_name, data, delta_s, gate_zone, timestamp
- `CheckpointManager`:
  - `save(step_name, data, delta_s, gate_zone)`
  - `restore(step_id)` → Checkpoint
  - `gate_check(from_zone, to_zone)` → bool
  - `list_checkpoints()` → List[Checkpoint]

实现 `coupler.py`:
- `ContractViolation` 异常
- `Coupler`:
  - `check_progression(current_delta, next_delta)` - ΔS下降或趋势向下才允许
  - `enforce_contract(current_delta, next_delta, local_force, global_tension)`
  - 强制局部移动与全局张力合约

实现 `semantic_firewall.py`:
- `FirewallResult`: decision, delta_s, step_results, corrections
- `SemanticFirewall`:
  - `check(text)` → FirewallResult
  - `check_with_pipeline(text)` → FirewallResult
  - 流程: 输入→ΔS→观变→坤守→巽调→复归→通过/拒绝/修正

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_reasoning/test_checkpoint.py tests/test_reasoning/test_coupler.py tests/test_reasoning/test_semantic_firewall.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/reasoning/checkpoint.py src/taiji_verify/reasoning/coupler.py src/taiji_verify/reasoning/semantic_firewall.py
git add tests/test_reasoning/test_checkpoint.py tests/test_reasoning/test_coupler.py tests/test_reasoning/test_semantic_firewall.py
git commit -m "feat(reasoning): add checkpoint, coupler, and semantic firewall"
```

---

## Task 7: Layer 4 Diagnosis层 - 全局修复图

### 文件
- Create: `src/taiji_verify/diagnosis/__init__.py`
- Create: `src/taiji_verify/diagnosis/global_fix_map.py`
- Create: `data/fix_map_entries.json`
- Create: `tests/test_diagnosis/test_global_fix_map.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_diagnosis/test_global_fix_map.py
import pytest
from taiji_verify.diagnosis.global_fix_map import FixEntry, GlobalFixMap

class TestGlobalFixMap:
    def test_load_fix_entries(self):
        fix_map = GlobalFixMap()
        assert len(fix_map.entries) > 0

    def test_get_by_category(self):
        fix_map = GlobalFixMap()
        entries = fix_map.get_by_category("Embeddings")
        assert all(e.category == "Embeddings" for e in entries)

    def test_get_by_failure_mode(self):
        fix_map = GlobalFixMap()
        entries = fix_map.get_by_failure_mode("FM01")
        assert all("FM01" in e.failure_mode_id for e in entries)

    def test_search_fixes(self):
        fix_map = GlobalFixMap()
        results = fix_map.search("embedding")
        assert len(results) > 0

    def test_fix_entry_structure(self):
        entry = FixEntry(
            id="F001",
            category="Embeddings",
            failure_mode_id="FM01",
            description="优化embedding质量",
            priority=3,
            steps=["step1", "step2"],
            references=["ref1"]
        )
        assert entry.priority == 3
        assert len(entry.steps) == 2
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_diagnosis/test_global_fix_map.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `global_fix_map.py`:
- `FixEntry`: id, category, failure_mode_id, description, priority, steps, references
- `GlobalFixMap`:
  - `__init__(data_path="data/fix_map_entries.json")`
  - `get_by_category(category)` → List[FixEntry]
  - `get_by_failure_mode(fm_id)` → List[FixEntry]
  - `search(query)` → List[FixEntry]
  - `get_fix(entry_id)` → FixEntry

创建 `data/fix_map_entries.json`:
- 7大类别，300+条目
- Embeddings(30+), Chunking(20+), RAG(50+), Language(30+)
- Reasoning&Memory(40+), Multi-Agent(30+), 其他

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_diagnosis/test_global_fix_map.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/diagnosis/global_fix_map.py data/fix_map_entries.json tests/test_diagnosis/test_global_fix_map.py
git commit -m "feat(diagnosis): add global fix map with 300+ entries"
```

---

## Task 8: Layer 4 Diagnosis层 - 故障排除地图

### 文件
- Create: `src/taiji_verify/diagnosis/troubleshooting_atlas.py`
- Create: `tests/test_diagnosis/test_troubleshooting_atlas.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_diagnosis/test_troubleshooting_atlas.py
import pytest
from taiji_verify.diagnosis.troubleshooting_atlas import (
    TroubleshootingAtlas, DiagnosisNode, DiagnosisResult
)

class TestTroubleshootingAtlas:
    def test_diagnosis_tree_creation(self):
        atlas = TroubleshootingAtlas()
        tree = atlas.get_diagnosis_tree()
        assert tree is not None
        assert len(tree.children) > 0

    def test_diagnose(self):
        atlas = TroubleshootingAtlas()
        result = atlas.diagnose(
            symptom="检索结果不准确",
            context={"failure_mode": "FM01"}
        )
        assert result.primary_cause is not None
        assert len(result.recommended_fixes) > 0

    def test_rank_fixes(self):
        atlas = TroubleshootingAtlas()
        fixes = atlas.rank_fixes(
            failure_mode="FM01",
            priority_hint="high"
        )
        assert len(fixes) > 0
        assert fixes[0].priority <= fixes[1].priority if len(fixes) > 1 else True
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_diagnosis/test_troubleshooting_atlas.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `troubleshooting_atlas.py`:
- `DiagnosisNode`: symptom, possible_causes, recommended_fixes, children
- `DiagnosisResult`: primary_cause, all_causes, recommended_fixes, confidence
- `TroubleshootingAtlas`:
  - `get_diagnosis_tree()` → DiagnosisNode
  - `diagnose(symptom, context)` → DiagnosisResult
  - `rank_fixes(failure_mode, priority_hint)` → List[FixEntry]

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_diagnosis/test_troubleshooting_atlas.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/diagnosis/troubleshooting_atlas.py tests/test_diagnosis/test_troubleshooting_atlas.py
git commit -m "feat(diagnosis): add troubleshooting atlas with diagnosis routing"
```

---

## Task 9: Layer 5 Governance层 - 双图与治理门

### 文件
- Create: `src/taiji_verify/governance/__init__.py`
- Create: `src/taiji_verify/governance/twin_atlas.py`
- Create: `src/taiji_verify/governance/inverse_atlas.py`
- Create: `src/taiji_verify/governance/governance_gates.py`
- Create: `tests/test_governance/test_twin_atlas.py`
- Create: `tests/test_governance/test_governance_gates.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_governance/test_twin_atlas.py
import pytest
from taiji_verify.governance.twin_atlas import TwinAtlas, AtlasResult

class TestTwinAtlas:
    def test_forward_routing(self):
        atlas = TwinAtlas()
        result = atlas.forward_route("碳排放权交易分析")
        assert result.target_domain is not None
        assert len(result.route_path) > 0

    def test_inverse_validation(self):
        atlas = TwinAtlas()
        result = atlas.inverse_validate("碳排放权交易分析")
        assert result.is_valid is not None

    def test_full_atlas_execution(self):
        atlas = TwinAtlas()
        result = atlas.execute("碳排放权交易分析")
        assert result.forward_result is not None
        assert result.inverse_result is not None

# tests/test_governance/test_governance_gates.py
import pytest
from taiji_verify.governance.governance_gates import (
    GovernanceGate, GateType, GateResult, GateState
)

class TestGovernanceGates:
    def test_gate1_problem_formation(self):
        gate = GovernanceGate(GateType.PROBLEM_FORMATION)
        result = gate.evaluate("碳排放权交易平台的监管问题")
        assert isinstance(result.state, GateState)

    def test_gate2_world_alignment(self):
        gate = GovernanceGate(GateType.WORLD_ALIGNMENT)
        result = gate.evaluate("地球是圆的")
        assert result.passed is True

    def test_gate3_collapse_geometry(self):
        gate = GovernanceGate(GateType.COLLAPSE_GEOMETRY)
        result = gate.evaluate("检测崩溃迹象")
        assert isinstance(result.state, GateState)

    def test_all_7_gates(self):
        gates = [GovernanceGate(gt) for gt in GateType]
        assert len(gates) == 7
        for gate in gates:
            result = gate.evaluate("测试输入")
            assert isinstance(result.passed, bool)
            assert result.reason is not None

    def test_gate_result_structure(self):
        gate = GovernanceGate(GateType.PROBLEM_FORMATION)
        result = gate.evaluate("有效问题")
        assert hasattr(result, 'passed')
        assert hasattr(result, 'state')
        assert hasattr(result, 'reason')
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_governance/test_twin_atlas.py tests/test_governance/test_governance_gates.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `governance_gates.py`:
- `GateType`: PROBLEM_FORMATION, WORLD_ALIGNMENT, COLLAPSE_GEOMETRY, ADJACENT_CUT, RESOLUTION_AUTH, FIX_LEGALITY, EMISSION_CONTROL
- `GateState`: STOP, COARSE, UNRESOLVED, AUTHORIZED
- `GateResult`: passed, state, reason, details
- `GovernanceGate`:
  - `__init__(gate_type)`
  - `evaluate(input_text, context)` → GateResult
  - 每个门有独立判定规则

实现 `twin_atlas.py`:
- `AtlasResult`: forward_result, inverse_result, coupled
- `TwinAtlas`:
  - `forward_route(input)` → ForwardResult
  - `inverse_validate(input)` → InverseResult
  - `execute(input)` → AtlasResult
  - Forward Atlas(路由发现) + Bridge(耦合层) + Inverse Atlas(逆向治理)

实现 `inverse_atlas.py`:
- `InverseAtlas`:
  - `validate_problem(input)` → bool
  - `check_world_facts(input)` → bool
  - `detect_collapse_signals(input)` → bool

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_governance/test_twin_atlas.py tests/test_governance/test_governance_gates.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/governance/twin_atlas.py src/taiji_verify/governance/inverse_atlas.py src/taiji_verify/governance/governance_gates.py
git add tests/test_governance/test_twin_atlas.py tests/test_governance/test_governance_gates.py
git commit -m "feat(governance): add twin atlas and 7 governance gates"
```

---

## Task 10: Layer 6 Execution层 - 目标编译器扩展

### 文件
- Create: `src/taiji_verify/execution/__init__.py`
- Create: `src/taiji_verify/execution/goal_compiler.py`
- Create: `src/taiji_verify/execution/task_atoms.py`
- Create: `src/taiji_verify/execution/execution_token.py`
- Create: `src/taiji_verify/execution/leak_auditor.py`
- Create: `tests/test_execution/test_goal_compiler.py`
- Create: `tests/test_execution/test_leak_auditor.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_execution/test_goal_compiler.py
import pytest
from taiji_verify.execution.goal_compiler import GoalCompiler, TruthObject

class TestGoalCompiler:
    def test_create_truth_objects(self):
        compiler = GoalCompiler()
        objects = compiler.create_truth_objects("碳排放权交易管理办法")
        assert len(objects) > 0
        assert all(isinstance(obj, TruthObject) for obj in objects)

    def test_create_claim_ceilings(self):
        compiler = GoalCompiler()
        ceilings = compiler.create_claim_ceilings("碳排放权交易")
        assert len(ceilings) > 0

    def test_extended_compile(self):
        compiler = GoalCompiler()
        result = compiler.compile_extended("分析碳排放权交易政策")
        assert result.truth_objects is not None
        assert result.verification_gates is not None

# tests/test_execution/test_leak_auditor.py
import pytest
from taiji_verify.execution.leak_auditor import LeakAuditor, AuditResult

class TestLeakAuditor:
    def test_check_upstream_completion(self):
        auditor = LeakAuditor()
        result = auditor.check("layer_2_detection", "output_text")
        assert isinstance(result, AuditResult)
        assert hasattr(result, 'leak_detected')

    def test_block_downstream_if_incomplete(self):
        auditor = LeakAuditor()
        auditor.mark_incomplete("layer_2")
        result = auditor.check("layer_3_reasoning", "output")
        assert result.leak_detected is True

    def test_allow_downstream_when_complete(self):
        auditor = LeakAuditor()
        auditor.mark_complete("layer_2")
        result = auditor.check("layer_3_reasoning", "output")
        assert result.leak_detected is False
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_execution/test_goal_compiler.py tests/test_execution/test_leak_auditor.py -v
```

- [ ] **Step 3: 实现源代码**

实现 `goal_compiler.py`:
- 扩展现有 PolarisCompiler
- `TruthObject`: id, content, verification_criteria, confidence
- `ClaimCeiling`: id, claim, max_confidence, required_sources
- `VerificationGate`: id, criteria, threshold, passed
- `GoalCompiler`:
  - `create_truth_objects(goal)` → List[TruthObject]
  - `create_claim_ceilings(goal)` → List[ClaimCeiling]
  - `create_verification_gates(goal)` → List[VerificationGate]
  - `compile_extended(goal)` → ExtendedCompilationResult

实现 `task_atoms.py`:
- 扩展 TaskAtom 增加 verification_gates, truth_objects, claim_ceilings

实现 `execution_token.py`:
- `ExecutionTokenBoard`: 令牌板管理
- `acquire_token(atom_id)` → ExecutionToken
- `release_token(token_id)`
- 每轮只执行一个解锁原子

实现 `leak_auditor.py`:
- `AuditResult`: leak_detected, upstream_status, reason
- `LeakAuditor`:
  - `mark_complete(layer_name)`
  - `mark_incomplete(layer_name)`
  - `check(layer_name, output)` → AuditResult
  - 防止上游未验证完成时启动下游工作

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_execution/test_goal_compiler.py tests/test_execution/test_leak_auditor.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/execution/ tests/test_execution/
git commit -m "feat(execution): add goal compiler extension and leak auditor"
```

---

## Task 11: 主引擎重写 - 六层融合

### 文件
- Modify: `src/taiji_verify/engine.py`
- Modify: `tests/test_engine.py`

- [ ] **Step 1: 编写失败的测试**

```python
# tests/test_engine.py (扩展)
class TestTaijiVerifyEngineV2:
    def test_verify_text_only(self):
        engine = TaijiVerifyEngine()
        response = engine.verify_text_only("碳排放权交易管理办法规定")
        assert isinstance(response.verdict, Verdict)
        assert response.verdict in [Verdict.PASS, Verdict.BLOCK, Verdict.CONDITIONAL_PASS]

    def test_verify_with_vectors(self):
        engine = TaijiVerifyEngine()
        input_vec = np.random.randn(128).astype(np.float32)
        ground_vec = np.random.randn(128).astype(np.float32)
        response = engine.verify_with_vectors(input_vec, ground_vec)
        assert isinstance(response.verdict, Verdict)

    def test_governance_gate_block(self):
        engine = TaijiVerifyEngine()
        engine.governance_enabled = True
        response = engine.verify_text_only("无效问题")
        if response.governance_result:
            if any(g.state == GateState.STOP for g in response.governance_result):
                assert response.verdict == Verdict.BLOCK

    def test_full_pipeline_verdict(self):
        engine = TaijiVerifyEngine()
        response = engine.verify_full_pipeline(
            input_text="碳排放权交易平台应当建立",
            ground_truth="碳排放权交易平台应当建立完善的监管机制"
        )
        assert response.verdict in [Verdict.PASS, Verdict.CONDITIONAL_PASS, Verdict.CORRECTED, Verdict.BLOCK, Verdict.ESCALATE]
```

- [ ] **Step 2: 运行测试验证失败**

```bash
pytest tests/test_engine.py -v
```

- [ ] **Step 3: 重写主引擎**

重写 `engine.py`:
- 集成所有6层模块
- `TaijiVerifyEngine`:
  - `verify(input_text, ground_truth, context, embed_fn, samples)` → VerificationResponse
  - `verify_text_only(input_text)` → VerificationResponse
  - `verify_with_vectors(input_vec, ground_vec)` → VerificationResponse
  - `verify_full_pipeline(input_text, ground_truth, context)` → VerificationResponse

判定规则:
```
治理层STOP → BLOCK
治理层COARSE → CONDITIONAL_PASS
CRITICAL失败模式 → BLOCK
ΔS在DANGER+检测高风险 → BLOCK
ΔS在RISK+修正成功 → CORRECTED
ΔS在RISK+修正失败 → ESCALATE
ΔS在TRANSIT → CONDITIONAL_PASS
ΔS在SAFE+低风险 → PASS
执行层有未完成 → CONDITIONAL_PASS
```

- [ ] **Step 4: 运行测试验证通过**

```bash
pytest tests/test_engine.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/taiji_verify/engine.py tests/test_engine.py
git commit -m "feat(engine): rewrite engine with 6-layer fusion"
```

---

## Task 12: 质量验收

### 验收标准

- [ ] **Step 1: 包名统一检查**

```bash
grep -r "taiji_agent\|opentaiji" src/ --include="*.py"
```
Expected: 无结果

- [ ] **Step 2: Import测试**

```bash
python -c "import taiji_verify; print('OK')"
```
Expected: OK

- [ ] **Step 3: 全量测试**

```bash
pytest tests/ -v --cov=taiji_verify --cov-report=term-missing
```
Expected: 覆盖率 ≥ 95%

- [ ] **Step 4: 16失败模式检测测试**

```bash
pytest tests/ -k "failure_mode or symptom" -v
```
Expected: 全部通过

- [ ] **Step 5: 7步推理链端到端测试**

```bash
pytest tests/test_reasoning/test_seven_step_chain.py -v
```
Expected: PASS

- [ ] **Step 6: 7治理门独立测试**

```bash
pytest tests/test_governance/test_governance_gates.py -v
```
Expected: 全部7个门可独立测试

- [ ] **Step 7: 5条生态规则测试**

```bash
pytest tests/test_detection/test_eco_rules.py -v
```
Expected: 5条规则可运行

- [ ] **Step 8: 3种相似度算法测试**

```bash
pytest tests/test_detection/test_consistency.py -v
```
Expected: Jaccard/Levenshtein/Cosine 全部通过

- [ ] **Step 9: 提交最终版本**

```bash
git add -A
git commit -m "feat: complete Taiji Verify 6-layer architecture"
```

---

## 质量验收标准清单

| # | 标准 | 验收命令 |
|---|------|----------|
| 1 | 包名统一taiji_verify | grep无残留 |
| 2 | 0个import错误 | python -c "import taiji_verify" |
| 3 | 全量测试≥95% | pytest --cov |
| 4 | 每模块≥90% | 分模块统计 |
| 5 | 16失败模式可检测 | 集成测试 |
| 6 | 7步推理链可执行 | 端到端测试 |
| 7 | 7治理门可独立测 | 单元测试 |
| 8 | 5条生态规则可运行 | 规则测试 |
| 9 | 3种相似度算法 | 一致性测试 |
| 10 | 零硬依赖taiji-agent | import检查 |

---

## 实施检查清单

- [ ] 所有Task完成并测试通过
- [ ] 覆盖率达标 95%+
- [ ] 无taiji-agent硬依赖
- [ ] 所有import正确
- [ ] 文档更新（如需要）
- [ ] 最终git commit

---

## 注意事项

1. 每个Task独立可测试
2. 遵循TDD: 先写测试，再实现
3. 代码风格与现有代码保持一致
4. 不添加不必要的注释
5. 每个模块有独立的__init__.py
6. 测试文件与源代码一一对应
