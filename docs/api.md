# Taiji Verify API 参考文档

版本：2.0 | 日期：2026-05-16

## 目录

1. [引擎层 (Engine)](#引擎层-engine)
2. [检测层 (Detection)](#检测层-detection)
3. [推理层 (Reasoning)](#推理层-reasoning)
4. [诊断层 (Diagnosis)](#诊断层-diagnosis)
5. [治理层 (Governance)](#治理层-governance)
6. [执行层 (Execution)](#执行层-execution)
7. [Embedding提供者](#embedding提供者)
8. [核心模块](#核心模块)

---

## 引擎层 (Engine)

### TaijiVerifyEngine

太极验证引擎主入口，整合六层架构的完整验证流水线。

```python
from taiji_verify.engine import TaijiVerifyEngine, Verdict

engine = TaijiVerifyEngine(
    embedding_dim=768,           # 向量维度，默认768
    delta_s_safe_threshold=0.3,  # ΔS安全阈值，默认0.3
    enable_all_layers=True,      # 启用全部六层，默认True
    enable_governance=True,      # 启用治理层，默认True
)
```

#### 方法

##### verify()

执行完整验证流水线。

```python
def verify(
    self,
    input_text: str,
    ground_truth: Optional[str] = None,
    context: Optional[dict] = None,
    embed_fn: Optional[Callable] = None,
    samples: Optional[int] = None,
) -> VerificationResponse
```

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| input_text | str | 必填 | 待验证的输入文本 |
| ground_truth | str | None | 标准答案/真值文本 |
| context | dict | None | 额外上下文信息 |
| embed_fn | Callable | None | 文本嵌入函数 |
| samples | int | None | 扰动采样数量 |

**返回值：** `VerificationResponse` 对象

**示例：**

```python
response = engine.verify(
    input_text="碳排放权交易管理办法规定...",
    ground_truth="碳排放权交易管理办法...",
)
print(f"判定: {response.verdict}")
```

---

##### verify_with_vectors()

使用预计算的向量进行验证。

```python
def verify_with_vectors(
    self,
    input_vec: np.ndarray,
    ground_vec: np.ndarray,
) -> VerificationResponse
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| input_vec | np.ndarray | 输入向量 |
| ground_vec | np.ndarray | 真值向量 |

**返回值：** `VerificationResponse` 对象

---

##### verify_text_only()

纯文本验证（不计算向量）。

```python
def verify_text_only(self, input_text: str) -> VerificationResponse
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| input_text | str | 待验证文本 |

**返回值：** `VerificationResponse` 对象

---

##### verify_full_pipeline()

完整流水线验证（verify的别名）。

```python
def verify_full_pipeline(
    self,
    input_text: str,
    ground_truth: Optional[str] = None,
    context: Optional[dict] = None,
) -> VerificationResponse
```

---

### Verdict

验证判定枚举。

```python
from taiji_verify.engine import Verdict

class Verdict(str, Enum):
    PASS = "pass"              # 通过
    CONDITIONAL_PASS = "conditional_pass"  # 有条件通过
    CORRECTED = "corrected"    # 修正后通过
    BLOCK = "block"            # 阻断
    ESCALATE = "escalate"      # 升级处理
```

---

### VerificationResponse

验证响应数据结构。

```python
@dataclass
class VerificationResponse:
    verdict: Verdict                           # 最终判定
    delta_s_result: Optional[DeltaSResult]     # ΔS计算结果
    detection_result: Optional[dict]          # 检测层结果
    reasoning_chain_result: Optional[dict]     # 推理层结果
    governance_result: Optional[dict]          # 治理层结果
    diagnosis_result: Optional[dict]           # 诊断层结果
    failure_detections: list[FailureDetection] # 失败检测列表
    compilation: Optional[CompilationResult]    # 目标编译结果
    final_vector: Optional[np.ndarray]         # 最终向量
    corrected_text: Optional[str]              # 修正后的文本
    processing_time_ms: int                    # 处理耗时(ms)
    metadata: dict                              # 元数据

    @property
    def is_passing(self) -> bool:
        return self.verdict in (Verdict.PASS, Verdict.CONDITIONAL_PASS, Verdict.CORRECTED)
```

---

## 检测层 (Detection)

### RuleEngine

规则引擎，检测文本中的环境领域规则违规。

```python
from taiji_verify.detection.rule_engine import RuleEngine

engine = RuleEngine()
```

#### 方法

##### verify()

```python
def verify(self, text: str) -> RuleEngineResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待检测文本 |

**返回值：** `RuleEngineResult` 对象

**示例：**

```python
result = engine.verify("该项目符合GB99999-9999标准")
print(f"违规规则: {result.violations}")
```

---

##### add_rule()

```python
def add_rule(self, rule: Rule) -> None
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| rule | Rule | 要添加的规则 |

---

##### add_knowledge_entry()

```python
def add_knowledge_entry(
    self,
    entry_id: str,
    content: str,
    keywords: list[str],
) -> None
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| entry_id | str | 知识条目ID |
| content | str | 知识内容 |
| keywords | list[str] | 关键词列表 |

---

### HallucinationDetector

幻觉检测器，检测文本中的幻觉内容。

```python
from taiji_verify.detection.hallucination_detector import (
    HallucinationDetector,
    RiskLevel,
)

detector = HallucinationDetector()
```

#### 方法

##### detect()

```python
def detect(self, text: str) -> HallucinationResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待检测文本 |

**返回值：** `HallucinationResult` 对象

---

### SelfConsistencyChecker

自一致性检查器。

```python
from taiji_verify.detection.consistency import SelfConsistencyChecker

checker = SelfConsistencyChecker()
```

#### 方法

##### batch_consistency()

```python
def batch_consistency(self, texts: list[str]) -> ConsistencyResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| texts | list[str] | 文本列表 |

**返回值：** `ConsistencyResult` 对象

---

### SourceTracer

来源追溯器。

```python
from taiji_verify.detection.source_tracer import SourceTracer

tracer = SourceTracer()
```

#### 方法

##### trace()

```python
def trace(self, claim: str) -> SourceTraceResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| claim | str | 待追溯的声明 |

**返回值：** `SourceTraceResult` 对象

---

## 推理层 (Reasoning)

### SevenStepChain

七步推理链，核心推理引擎。

```python
from taiji_verify.reasoning.seven_step_chain import SevenStepChain, StepInput

chain = SevenStepChain()
```

#### 方法

##### execute_full_chain()

```python
def execute_full_chain(
    self,
    input_data: StepInput,
) -> ChainResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| input_data | StepInput | 包含text和goal的输入数据 |

**返回值：** `ChainResult` 对象

**示例：**

```python
from taiji_verify.reasoning.seven_step_chain import StepInput

result = chain.execute_full_chain(StepInput(
    text="碳排放权交易管理办法规定...",
    goal="碳排放权交易管理办法...",
))
print(f"最终ΔS: {result.final_delta_s}")
```

---

### SemanticFirewall

语义防火墙。

```python
from taiji_verify.reasoning.semantic_firewall import SemanticFirewall

firewall = SemanticFirewall()
```

#### 方法

##### check()

```python
def check(self, text: str) -> FirewallResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待检查文本 |

**返回值：** `FirewallResult` 对象

---

### Coupler

耦合器，确保推理步骤之间的耦合度。

```python
from taiji_verify.reasoning.coupler import Coupler

coupler = Coupler()
```

#### 方法

##### check_coupling()

```python
def check_coupling(
    self,
    previous_step: str,
    current_step: str,
) -> CouplingResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| previous_step | str | 前一步骤 |
| current_step | str | 当前步骤 |

**返回值：** `CouplingResult` 对象

---

### Checkpoint

检查点管理器。

```python
from taiji_verify.reasoning.checkpoint import Checkpoint

checkpoint = Checkpoint()
```

#### 方法

##### save()

```python
def save(self, state: dict) -> str
```

**返回值：** 检查点ID

---

##### restore()

```python
def restore(self, checkpoint_id: str) -> dict
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| checkpoint_id | str | 检查点ID |

**返回值：** 保存的状态

---

## 诊断层 (Diagnosis)

### GlobalFixMap

全局修复映射表。

```python
from taiji_verify.diagnosis.global_fix_map import GlobalFixMap

fix_map = GlobalFixMap()
```

#### 方法

##### get_by_category()

```python
def get_by_category(
    self,
    category: str,
) -> list[FixSuggestion]
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| category | str | 修复类别 |

**返回值：** 修复建议列表

---

##### get_fixes()

```python
def get_fixes(
    self,
    failure_mode: str,
) -> list[FixSuggestion]
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| failure_mode | str | 失败模式 |

**返回值：** 修复建议列表

---

### TroubleshootingAtlas

故障排除图谱。

```python
from taiji_verify.diagnosis.troubleshooting_atlas import TroubleshootingAtlas

atlas = TroubleshootingAtlas()
```

#### 方法

##### diagnose()

```python
def diagnose(self, text: str) -> DiagnosisResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待诊断文本 |

**返回值：** `DiagnosisResult` 对象

---

## 治理层 (Governance)

### GovernanceGate

治理门，评估输入是否满足治理要求。

```python
from taiji_verify.governance.governance_gates import (
    GovernanceGate,
    GateType,
    GateState,
    GateResult,
    evaluate_all_gates,
)

gate = GovernanceGate(GateType.WORLD_ALIGNMENT)
```

#### 门类型 (GateType)

```python
class GateType(str, Enum):
    PROBLEM_FORMATION = "problem_formation"       # 问题构成
    WORLD_ALIGNMENT = "world_alignment"           # 世界对齐
    COLLAPSE_GEOMETRY = "collapse_geometry"       # 崩溃几何
    ADJACENT_CUT = "adjacent_cut"                 # 相邻切割
    RESOLUTION_AUTH = "resolution_auth"           # 解决授权
    FIX_LEGALITY = "fix_legality"                 # 修复合法性
    EMISSION_CONTROL = "emission_control"          # Emission控制
```

#### 门状态 (GateState)

```python
class GateState(str, Enum):
    STOP = "stop"         # 停止/阻断
    COARSE = "coarse"     # 粗糙/有条件通过
    UNRESOLVED = "unresolved"  # 未解决
    AUTHORIZED = "authorized"  # 授权通过
```

#### 方法

##### evaluate()

```python
def evaluate(
    self,
    input_text: str,
    context: Optional[dict] = None,
) -> GateResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| input_text | str | 待评估文本 |
| context | dict | 上下文信息 |

**返回值：** `GateResult` 对象

**示例：**

```python
result = gate.evaluate("地球是圆的")
print(f"状态: {result.state}")
print(f"原因: {result.reason}")
```

---

##### evaluate_all_gates()

评估所有7个治理门。

```python
def evaluate_all_gates(input_text: str) -> dict[GateType, GateResult]
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| input_text | str | 待评估文本 |

**返回值：** 门类型到结果的字典

---

### TwinAtlas

双图，正向路由和逆向验证。

```python
from taiji_verify.governance.twin_atlas import TwinAtlas

atlas = TwinAtlas()
```

#### 方法

##### execute()

```python
def execute(self, text: str) -> AtlasResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待分析文本 |

**返回值：** `AtlasResult` 对象

---

### InverseAtlas

逆图，逆向验证推理链。

```python
from taiji_verify.governance.inverse_atlas import InverseAtlas

inverse_atlas = InverseAtlas()
```

#### 方法

##### validate()

```python
def validate(
    self,
    text: str,
    requires_premises: Optional[list[str]] = None,
) -> InverseResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待验证文本 |
| requires_premises | list[str] | 必需的前提条件 |

**返回值：** `InverseResult` 对象

---

##### detect_gaps()

```python
def detect_gaps(
    self,
    text: str,
    evidence: str = "",
) -> list[LogicalGap]
```

**参数：**

| 参数 |类型 | 描述 |
|------|------|------|
| text | str | 待检测文本 |
| evidence | str | 证据文本 |

**返回值：** 逻辑间隙列表

---

## 执行层 (Execution)

### GoalCompiler

目标编译器，将目标编译为任务图。

```python
from taiji_verify.execution.goal_compiler import GoalCompiler, TaskType, TaskState

compiler = GoalCompiler()
```

#### 任务类型 (TaskType)

```python
class TaskType(str, Enum):
    ATOMIC = "atomic"       # 原子任务
    SEQUENCE = "sequence"   # 序列任务
    PARALLEL = "parallel"   # 并行任务
    CONDITIONAL = "conditional"  # 条件任务
```

#### 任务状态 (TaskState)

```python
class TaskState(str, Enum):
    PENDING = "pending"     # 待执行
    RUNNING = "running"     # 执行中
    COMPLETED = "completed" # 已完成
    FAILED = "failed"       # 失败
```

#### 方法

##### compile()

```python
def compile(self, goal: str) -> CompilationResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| goal | str | 目标描述 |

**返回值：** `CompilationResult` 对象

**示例：**

```python
result = compiler.compile("完成环境影响评价报告")
print(f"任务数: {len(result.task_graph)}")
```

---

### LeakAuditor

泄漏审计器，检查敏感信息泄漏。

```python
from taiji_verify.execution.leak_auditor import LeakAuditor

auditor = LeakAuditor()
```

#### 方法

##### check()

```python
def check(self, text: str) -> LeakCheckResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待检查文本 |

**返回值：** `LeakCheckResult` 对象

---

## Embedding提供者

### EmbeddingProvider (ABC)

Embedding提供者抽象基类。

```python
from taiji_verify.embedding import (
    EmbeddingProvider,
    SimpleBagOfWordsProvider,
)

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        """文本→向量"""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        """批量文本→向量"""
```

---

### SimpleBagOfWordsProvider

词袋模型嵌入提供者（零依赖）。

```python
from taiji_verify.embedding import SimpleBagOfWordsProvider

provider = SimpleBagOfWordsProvider(
    dimension=768,     # 向量维度，默认768
    stopwords=None,   # 停用词列表
)
```

#### 方法

##### embed()

```python
def embed(self, text: str) -> np.ndarray
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 输入文本 |

**返回值：** 嵌入向量 (numpy.ndarray)

---

##### embed_batch()

```python
def embed_batch(self, texts: list[str]) -> list[np.ndarray]
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| texts | list[str] | 文本列表 |

**返回值：** 嵌入向量列表

---

### OpenAIEmbeddingProvider

OpenAI嵌入提供者。

```python
from taiji_verify.embedding import OpenAIEmbeddingProvider

provider = OpenAIEmbeddingProvider(
    api_key="your-api-key",  # OpenAI API密钥
    model="text-embedding-3-small",  # 模型名称
)
```

---

### LocalSentenceTransformerProvider

本地Sentence Transformer提供者。

```python
from taiji_verify.embedding import LocalSentenceTransformerProvider

provider = LocalSentenceTransformerProvider(
    model_name="paraphrase-multilingual-mpnet-base-v2",  # 模型名称
)
```

---

## 核心模块

### DeltaSCalculator

阴阳距计算器。

```python
from taiji_verify.delta_s import DeltaSCalculator, GateZone

calculator = DeltaSCalculator(
    embedding_dim=768,
    safe_threshold=0.3,
    transit_threshold=0.6,
    risk_threshold=0.85,
)
```

#### 方法

##### compute()

```python
def compute(
    self,
    output_vec: np.ndarray,
    ground_vec: np.ndarray,
) -> DeltaSResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| output_vec | np.ndarray | 输出向量 |
| ground_vec | np.ndarray | 真值向量 |

**返回值：** `DeltaSResult` 对象

---

### KunGuard

坤守修正器。

```python
from taiji_verify.kun_guard import KunGuard, HazardLevel

guard = KunGuard()
```

#### 方法

##### protect()

```python
def protect(
    self,
    text: str,
    delta_s: float,
) -> KunGuardResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待保护文本 |
| delta_s | float | 阴阳距 |

**返回值：** `KunGuardResult` 对象

---

### QianAdvance

乾进评估器。

```python
from taiji_verify.qian_advance import QianAdvance

advance = QianAdvance()
```

#### 方法

##### evaluate()

```python
def evaluate(
    self,
    text: str,
    base_delta_s: float,
    n_paths: int = 5,
) -> QianAdvanceResult
```

**参数：**

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| text | str | 必填 | 待评估文本 |
| base_delta_s | float | 必填 | 基准阴阳距 |
| n_paths | int | 5 | 扰动路径数 |

**返回值：** `QianAdvanceResult` 对象

---

### FuReturn

复归检测器。

```python
from taiji_verify.fu_return import FuReturn, RecoveryState

detector = FuReturn()
```

#### 方法

##### monitor_and_recover()

```python
def monitor_and_recover(
    self,
    delta_s: float,
    text: str,
) -> RecoveryResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| delta_s | float | 阴阳距 |
| text | str | 文本 |

**返回值：** `RecoveryResult` 对象

---

### XunTune

巽调优化器。

```python
from taiji_verify.xun_tune import XunTune

tuner = XunTune()
```

#### 方法

##### tune()

```python
def tune(
    self,
    weights: np.ndarray,
    delta_s: float,
) -> TunedOutput
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| weights | np.ndarray | 注意力权重 |
| delta_s | float | 阴阳距 |

**返回值：** `TunedOutput` 对象

---

### PolarisCompiler

北极星目标编译器。

```python
from taiji_verify.polaris import PolarisCompiler

compiler = PolarisCompiler()
```

#### 方法

##### compile_goal()

```python
def compile_goal(
    self,
    goal: str,
    task_type: Optional[str] = None,
) -> CompilationResult
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| goal | str | 目标描述 |
| task_type | str | 任务类型 |

**返回值：** `CompilationResult` 对象

---

### SymptomMap

症状映射表。

```python
from taiji_verify.symptom_map import SymptomMap

symptom_map = SymptomMap()
```

#### 方法

##### match()

```python
def match(
    self,
    text: str,
) -> list[FailureSymptom]
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待匹配文本 |

**返回值：** 匹配的症状列表

---

### FailureModeDetector

失败模式检测器。

```python
from taiji_verify.failure_modes import FailureModeDetector

detector = FailureModeDetector()
```

#### 方法

##### detect_all()

```python
def detect_all(self, text: str) -> list[FailureDetection]
```

**参数：**

| 参数 | 类型 | 描述 |
|------|------|------|
| text | str | 待检测文本 |

**返回值：** 失败检测列表

---

## 异常处理

Taiji Verify 使用以下自定义异常：

```python
from taiji_verify.exceptions import (
    TaijiVerifyError,
    ValidationError,
    ComputationError,
    TimeoutError,
)

try:
    response = engine.verify(text)
except ValidationError as e:
    print(f"验证错误: {e}")
except ComputationError as e:
    print(f"计算错误: {e}")
```

---

## 使用示例

### 基础使用

```python
from taiji_verify.engine import TaijiVerifyEngine, Verdict

engine = TaijiVerifyEngine()

response = engine.verify(
    input_text="碳排放权交易管理办法规定碳排放权交易应当遵守本办法。请问该项目的环境影响评价应该如何开展？",
    ground_truth="碳排放权交易管理办法规定...",
)

print(f"判定: {response.verdict}")
print(f"通过: {response.is_passing}")
print(f"耗时: {response.processing_time_ms}ms")
```

### 批量验证

```python
from taiji_verify.engine import TaijiVerifyEngine

engine = TaijiVerifyEngine()

texts = [
    "文本1...",
    "文本2...",
    "文本3...",
]

for text in texts:
    response = engine.verify(text)
    if not response.is_passing:
        print(f"发现问题: {text}")
```

### 自定义Embedding

```python
from taiji_verify.engine import TaijiVerifyEngine
from taiji_verify.embedding import SimpleBagOfWordsProvider

provider = SimpleBagOfWordsProvider(dimension=128)
engine = TaijiVerifyEngine(embedding_dim=128)

def embed_fn(text):
    return provider.embed(text)

response = engine.verify(
    input_text="...",
    ground_truth="...",
    embed_fn=embed_fn,
)
```

---

## 注意事项

1. **向量维度**：确保 `embedding_dim` 与 EmbeddingProvider 返回的向量维度一致
2. **线程安全**：`TaijiVerifyEngine` 实例在多线程环境下使用需要同步
3. **性能优化**：对于大量文本验证，考虑批量处理
4. **内存管理**：长时间运行时注意内存泄漏，定期创建新实例
5. **Embedding选择**：生产环境推荐使用 OpenAI 或 LocalSentenceTransformer

---

## 扩展指南

### 添加自定义规则

```python
from taiji_verify.detection.rule_engine import Rule, RuleEngine

class CustomRule(Rule):
    id = "custom_rule_001"
    name = "自定义规则"
    pattern = r"特定模式"
    severity = "HIGH"

engine = RuleEngine()
engine.add_rule(CustomRule())
```

### 添加自定义失败模式

```python
from taiji_verify.failure_modes import FailureMode, FailureModeDetector

class CustomFailure(FailureMode):
    id = "CF01"
    name = "自定义失败"
    severity = FailureSeverity.HIGH

detector = FailureModeDetector()
detector.register_mode(CustomFailure())
```
