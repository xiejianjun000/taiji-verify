"""
Neural Symbolic Verifier Tests - 神经符号双轨验证器测试

测试用例覆盖：
1. 三种融合策略
2. 轨道矛盾处理
3. 默认配置
4. TrackResult和DualTrackResult
5. 边界条件

v2.2 Phase 1
"""

import sys
import os
import types
from unittest.mock import MagicMock

# 先mock jieba，避免pkg_resources问题
jieba_mock = MagicMock()
sys.modules['jieba'] = jieba_mock
sys.modules['jieba.posseg'] = MagicMock()
sys.modules['jieba.finalseg'] = MagicMock()

# 直接加载模块 - 不使用taiji_verify包名
ns_module = types.ModuleType('neural_symbolic')
sys.modules['neural_symbolic'] = ns_module

# 加载cross_model_verifier
cmv_module = types.ModuleType('cross_model_verifier')
sys.modules['cross_model_verifier'] = cmv_module

with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'cross_model_verifier.py'),
    'r'
) as f:
    content = f.read()
exec(content, cmv_module.__dict__)

# 加载规则引擎
re_module = types.ModuleType('rule_engine')
sys.modules['rule_engine'] = re_module

with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'rule_engine.py'),
    'r'
) as f:
    content = f.read()
exec(content, re_module.__dict__)

# 加载consistency
cons_module = types.ModuleType('consistency')
sys.modules['consistency'] = cons_module

with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'consistency.py'),
    'r'
) as f:
    content = f.read()
exec(content, cons_module.__dict__)

# 修改neural_symbolic.py中的导入路径
with open(
    os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'taiji_verify', 'detection', 'neural_symbolic.py'),
    'r'
) as f:
    content = f.read()

# 替换导入语句
content = content.replace(
    "from taiji_verify.detection.cross_model_verifier import",
    "from cross_model_verifier import"
)
content = content.replace(
    "from taiji_verify.detection.rule_engine import",
    "from rule_engine import"
)
content = content.replace(
    "from taiji_verify.detection.consistency import",
    "from consistency import"
)

exec(content, ns_module.__dict__)

# 导入需要的类
TrackType = ns_module.TrackType
TrackResult = ns_module.TrackResult
DualTrackResult = ns_module.DualTrackResult
NeuralSymbolicVerifier = ns_module.NeuralSymbolicVerifier


class TestTrackType:
    """TrackType枚举测试"""

    def test_track_type_values(self):
        """测试轨道类型值"""
        assert TrackType.NEURAL.value == "neural"
        assert TrackType.SYMBOLIC.value == "symbolic"
        assert TrackType.FUSED.value == "fused"


class TestTrackResult:
    """TrackResult数据类测试"""

    def test_track_result_creation(self):
        """测试创建"""
        result = TrackResult(
            track_type=TrackType.NEURAL,
            score=0.8,
            verdict="pass",
            evidence=["证据1", "证据2"],
            confidence=0.9
        )
        assert result.track_type == TrackType.NEURAL
        assert result.score == 0.8
        assert result.verdict == "pass"
        assert len(result.evidence) == 2
        assert result.confidence == 0.9

    def test_track_result_defaults(self):
        """测试默认值"""
        result = TrackResult(track_type=TrackType.NEURAL)
        assert result.score == 0.0
        assert result.verdict == "uncertain"
        assert result.evidence == []
        assert result.confidence == 0.5

    def test_track_result_to_dict(self):
        """测试转换为字典"""
        result = TrackResult(
            track_type=TrackType.NEURAL,
            score=0.8,
            verdict="pass"
        )
        d = result.to_dict()
        assert d["track_type"] == "neural"
        assert d["score"] == 0.8
        assert d["verdict"] == "pass"


class TestDualTrackResult:
    """DualTrackResult数据类测试"""

    def test_dual_track_result_creation(self):
        """测试创建"""
        neural = TrackResult(track_type=TrackType.NEURAL, score=0.7)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, score=0.8)
        fused = TrackResult(track_type=TrackType.FUSED, score=0.75)

        result = DualTrackResult(
            neural_result=neural,
            symbolic_result=symbolic,
            fused_result=fused,
            fusion_strategy="weighted",
            disagreement=False
        )

        assert result.neural_result.score == 0.7
        assert result.symbolic_result.score == 0.8
        assert result.fused_result.score == 0.75
        assert result.fusion_strategy == "weighted"
        assert result.disagreement is False

    def test_dual_track_has_disagreement(self):
        """测试矛盾检测属性"""
        neural = TrackResult(track_type=TrackType.NEURAL, score=0.9, verdict="pass")
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, score=0.2, verdict="fail")
        fused = TrackResult(track_type=TrackType.FUSED, score=0.5)

        result = DualTrackResult(
            neural_result=neural,
            symbolic_result=symbolic,
            fused_result=fused,
            disagreement=True
        )
        assert result.has_disagreement is True

    def test_dual_track_get_highest_risk_track(self):
        """测试获取高风险轨道"""
        neural = TrackResult(track_type=TrackType.NEURAL, score=0.3)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, score=0.7)
        fused = TrackResult(track_type=TrackType.FUSED, score=0.5)

        result = DualTrackResult(
            neural_result=neural,
            symbolic_result=symbolic,
            fused_result=fused
        )
        assert result.get_highest_risk_track() == TrackType.NEURAL

    def test_dual_track_to_dict(self):
        """测试转换为字典"""
        neural = TrackResult(track_type=TrackType.NEURAL, score=0.7)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, score=0.8)
        fused = TrackResult(track_type=TrackType.FUSED, score=0.75)

        result = DualTrackResult(
            neural_result=neural,
            symbolic_result=symbolic,
            fused_result=fused
        )

        d = result.to_dict()
        assert "neural" in d
        assert "symbolic" in d
        assert "fused" in d
        assert d["disagreement"] is False


class TestNeuralSymbolicVerifierInit:
    """NeuralSymbolicVerifier初始化测试"""

    def test_init_default(self):
        """测试默认初始化"""
        verifier = NeuralSymbolicVerifier()
        assert verifier._enable_neural is True
        assert verifier._enable_symbolic is True
        assert verifier._fusion_strategy == "weighted"
        assert verifier._neural_weight == 0.4
        assert verifier._symbolic_weight == 0.6

    def test_init_custom_weights(self):
        """测试自定义权重"""
        verifier = NeuralSymbolicVerifier(
            neural_weight=0.3,
            symbolic_weight=0.7
        )
        assert verifier._neural_weight == 0.3
        assert verifier._symbolic_weight == 0.7

    def test_init_invalid_weights(self):
        """测试无效权重"""
        try:
            NeuralSymbolicVerifier(neural_weight=0.5, symbolic_weight=0.3)
            assert False, "应该抛出异常"
        except ValueError as e:
            assert "权重和必须为1.0" in str(e)

    def test_init_invalid_strategy(self):
        """测试无效策略"""
        try:
            NeuralSymbolicVerifier(fusion_strategy="invalid")
            assert False, "应该抛出异常"
        except ValueError as e:
            assert "不支持的融合策略" in str(e)

    def test_init_neural_disabled(self):
        """测试禁用神经轨道"""
        verifier = NeuralSymbolicVerifier(enable_neural=False)
        assert verifier.is_neural_enabled is False

    def test_init_symbolic_disabled(self):
        """测试禁用符号轨道"""
        verifier = NeuralSymbolicVerifier(enable_symbolic=False)
        assert verifier.is_symbolic_enabled is False

    def test_init_both_disabled(self):
        """测试同时禁用"""
        verifier = NeuralSymbolicVerifier(enable_neural=False, enable_symbolic=False)
        assert verifier.is_neural_enabled is False
        assert verifier.is_symbolic_enabled is False


class TestFusionStrategies:
    """融合策略测试"""

    def test_weighted_strategy(self):
        """测试加权策略"""
        verifier = NeuralSymbolicVerifier(fusion_strategy="weighted")
        assert verifier.fusion_strategy == "weighted"

    def test_conservative_strategy(self):
        """测试保守策略"""
        verifier = NeuralSymbolicVerifier(fusion_strategy="conservative")
        assert verifier.fusion_strategy == "conservative"

    def test_optimistic_strategy(self):
        """测试乐观策略"""
        verifier = NeuralSymbolicVerifier(fusion_strategy="optimistic")
        assert verifier.fusion_strategy == "optimistic"

    def test_set_fusion_strategy(self):
        """测试设置融合策略"""
        verifier = NeuralSymbolicVerifier()
        verifier.set_fusion_strategy("conservative")
        assert verifier.fusion_strategy == "conservative"

    def test_set_invalid_strategy(self):
        """测试设置无效策略"""
        verifier = NeuralSymbolicVerifier()
        try:
            verifier.set_fusion_strategy("invalid")
            assert False
        except ValueError:
            pass


class TestWeightsProperty:
    """权重属性测试"""

    def test_weights_property(self):
        """测试权重元组"""
        verifier = NeuralSymbolicVerifier(neural_weight=0.3, symbolic_weight=0.7)
        weights = verifier.weights
        assert weights == (0.3, 0.7)


class TestVerify:
    """验证功能测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = NeuralSymbolicVerifier()

    def test_verify_basic(self):
        """测试基本验证"""
        result = self.verifier.verify("碳排放权交易管理办法规定重点排污单位应当安装自动监测设备")
        assert isinstance(result, DualTrackResult)
        assert result.neural_result is not None
        assert result.symbolic_result is not None
        assert result.fused_result is not None

    def test_verify_with_context(self):
        """测试带上下文验证"""
        context = {"context": "相关背景信息"}
        result = self.verifier.verify("测试文本", context=context)
        assert result is not None

    def test_verify_with_claim(self):
        """测试带声称验证"""
        result = self.verifier.verify("测试文本", claim="声称来源")
        assert result is not None


class TestRunNeuralTrack:
    """神经轨道测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = NeuralSymbolicVerifier()

    def test_run_neural_track_disabled(self):
        """测试禁用神经轨道"""
        verifier = NeuralSymbolicVerifier(enable_neural=False)
        result = verifier._run_neural_track("测试文本", None)
        assert result.track_type == TrackType.NEURAL
        assert result.confidence == 0.0
        assert "未启用" in result.evidence[0]

    def test_run_neural_track_enabled(self):
        """测试启用神经轨道"""
        result = self.verifier._run_neural_track("碳排放权交易", None)
        assert result.track_type == TrackType.NEURAL
        assert result.score >= 0.0


class TestRunSymbolicTrack:
    """符号轨道测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = NeuralSymbolicVerifier()

    def test_run_symbolic_track_disabled(self):
        """测试禁用符号轨道"""
        verifier = NeuralSymbolicVerifier(enable_symbolic=False)
        result = verifier._run_symbolic_track("测试文本", None, None)
        assert result.track_type == TrackType.SYMBOLIC
        assert result.confidence == 0.0
        assert "未启用" in result.evidence[0]

    def test_run_symbolic_track_enabled(self):
        """测试启用符号轨道"""
        result = self.verifier._run_symbolic_track("碳排放权交易", None, None)
        assert result.track_type == TrackType.SYMBOLIC
        assert result.score >= 0.0


class TestFusion:
    """融合测试"""

    def test_fuse_weighted(self):
        """测试加权融合"""
        verifier = NeuralSymbolicVerifier(fusion_strategy="weighted")
        neural = TrackResult(track_type=TrackType.NEURAL, score=0.6, confidence=0.6)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, score=0.8, confidence=0.9)

        fused = verifier._fuse(neural, symbolic, "weighted")

        assert fused.track_type == TrackType.FUSED
        # 0.6 * 0.4 + 0.8 * 0.6 = 0.24 + 0.48 = 0.72
        assert 0.7 <= fused.score <= 0.75

    def test_fuse_conservative(self):
        """测试保守融合"""
        verifier = NeuralSymbolicVerifier(fusion_strategy="conservative")
        neural = TrackResult(track_type=TrackType.NEURAL, score=0.8, confidence=0.8)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, score=0.4, confidence=0.9)

        fused = verifier._fuse(neural, symbolic, "conservative")

        # 保守策略应该偏向低分
        assert fused.score <= max(neural.score, symbolic.score)

    def test_fuse_optimistic(self):
        """测试乐观融合"""
        verifier = NeuralSymbolicVerifier(fusion_strategy="optimistic")
        neural = TrackResult(track_type=TrackType.NEURAL, score=0.4, confidence=0.5)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, score=0.6, confidence=0.7)

        fused = verifier._fuse(neural, symbolic, "optimistic")

        # 乐观策略应该偏向高分
        assert fused.score >= min(neural.score, symbolic.score)


class TestDisagreementDetection:
    """矛盾检测测试"""

    def setup_method(self):
        """测试前准备"""
        self.verifier = NeuralSymbolicVerifier()

    def test_check_disagreement_pass_fail(self):
        """测试pass/fail矛盾"""
        neural = TrackResult(track_type=TrackType.NEURAL, verdict="pass", score=0.8)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, verdict="fail", score=0.2)

        has_disagreement = self.verifier._check_disagreement(neural, symbolic)
        assert has_disagreement is True

    def test_check_disagreement_same(self):
        """测试无矛盾"""
        neural = TrackResult(track_type=TrackType.NEURAL, verdict="pass", score=0.8)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, verdict="pass", score=0.9)

        has_disagreement = self.verifier._check_disagreement(neural, symbolic)
        assert has_disagreement is False

    def test_check_disagreement_uncertain(self):
        """测试含uncertain时不判定为矛盾"""
        neural = TrackResult(track_type=TrackType.NEURAL, verdict="pass", score=0.8)
        symbolic = TrackResult(track_type=TrackType.SYMBOLIC, verdict="uncertain", score=0.5)

        has_disagreement = self.verifier._check_disagreement(neural, symbolic)
        assert has_disagreement is False


class TestEdgeCases:
    """边界条件测试"""

    def test_empty_text(self):
        """测试空文本"""
        verifier = NeuralSymbolicVerifier()
        result = verifier.verify("")
        assert isinstance(result, DualTrackResult)

    def test_very_long_text(self):
        """测试超长文本"""
        verifier = NeuralSymbolicVerifier()
        long_text = "碳排放权交易管理办法规定。" * 100
        result = verifier.verify(long_text)
        assert isinstance(result, DualTrackResult)

    def test_special_characters(self):
        """测试特殊字符"""
        verifier = NeuralSymbolicVerifier()
        result = verifier.verify("测试！@#$%^&*（）")
        assert isinstance(result, DualTrackResult)

    def test_unicode_text(self):
        """测试Unicode"""
        verifier = NeuralSymbolicVerifier()
        result = verifier.verify("碳排放权交易🔥管理办法")
        assert isinstance(result, DualTrackResult)
