# Taiji Verify 架构说明

版本：2.0 | 日期：2026-05-16

## 设计理念

Taiji Verify 源自中国古代哲学"太极生两仪，两仪生四象，四象生八卦"的思想，将AI语义验证过程映射为八卦运转：

- **阴阳 (Yin-Yang)**: 输入与输出的对立统一
- **四象 (Sixiang)**: 四种安全区域（SAFE/TRANSIT/RISK/DANGER）
- **八卦 (Bagua)**: 八种验证状态与修正策略

## 六层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Layer 6: 执行层                           │
│              目标编译器(Polaris) | 泄漏审计(LeakAuditor)           │
├─────────────────────────────────────────────────────────────────┤
│                        Layer 5: 治理层                           │
│   双图(TwinAtlas) | 7个治理门(GovernanceGates)                   │
├─────────────────────────────────────────────────────────────────┤
│                        Layer 4: 诊断层                           │
│        全局修复图(GlobalFixMap) | 故障排除图谱(Troubleshooting)    │
├─────────────────────────────────────────────────────────────────┤
│                        Layer 3: 推理层                           │
│  七步链(SevenStepChain) | 语义防火墙(SemanticFirewall) | 耦合器    │
├─────────────────────────────────────────────────────────────────┤
│                        Layer 2: 检测层                           │
│    规则引擎(RuleEngine) | 幻觉检测(Hallucination) | 溯源(Source)   │
├─────────────────────────────────────────────────────────────────┤
│                        Layer 1: 核心层                           │
│        ΔS计算 | 坤守 | 乾进 | 复归 | 巽调 | 北极星编译            │
└─────────────────────────────────────────────────────────────────┘
```

### Layer 1: 核心层

| 模块 | 描述 |
|------|------|
| DeltaSCalculator | 阴阳距计算，衡量输入与真值的语义距离 |
| KunGuard | 坤卦主承载，对高风险输出进行修正 |
| QianAdvance | 乾卦主进取，评估多路径扰动稳定性 |
| FuReturn | 复卦主回归，检测崩溃并触发恢复 |
| XunTune | 巽卦主调适，动态调整注意力权重 |
| PolarisCompiler | 北极星目标编译器，编译任务图 |

### Layer 2: 检测层

| 模块 | 描述 |
|------|------|
| RuleEngine | 环境领域规则引擎，检测GB标准合规性 |
| HallucinationDetector | 幻觉检测，识别无依据声明 |
| SelfConsistencyChecker | 自一致性检查 |
| SourceTracer | 来源追溯 |

### Layer 3: 推理层

| 模块 | 描述 |
|------|------|
| SevenStepChain | 七步推理链：盘古→开阳→玉衡→天枢→摇光→北极→天权 |
| SemanticFirewall | 语义防火墙，检查逻辑完整性 |
| Coupler | 耦合器，确保步骤间连贯性 |
| Checkpoint | 检查点管理，支持回滚 |

### Layer 4: 诊断层

| 模块 | 描述 |
|------|------|
| GlobalFixMap | 全局修复映射表，16类失败模式→修复方案 |
| TroubleshootingAtlas | 故障排除图谱，推理故障根因 |

### Layer 5: 治理层

| 模块 | 描述 |
|------|------|
| TwinAtlas | 双图：Forward路由 + Inverse验证 |
| GovernanceGates | 7个治理门 |

#### 7个治理门

| 门类型 | 描述 | 输出状态 |
|--------|------|----------|
| PROBLEM_FORMATION | 问题是否有效形成 | STOP/COARSE/AUTHORIZED |
| WORLD_ALIGNMENT | 是否与已知事实对齐 | STOP/AUTHORIZED |
| COLLAPSE_GEOMETRY | 是否有崩溃迹象 | STOP/COARSE/AUTHORIZED |
| ADJACENT_CUT | 是否与相邻领域冲突 | COARSE/AUTHORIZED |
| RESOLUTION_AUTH | 是否赢得存在权利 | COARSE/UNRESOLVED/AUTHORIZED |
| FIX_LEGALITY | 修正是否合法 | STOP/AUTHORIZED |
| EMISSION_CONTROL | 是否可公开发布 | STOP/AUTHORIZED |

### Layer 6: 执行层

| 模块 | 描述 |
|------|------|
| GoalCompiler | 目标编译器，将目标编译为TaskAtom任务图 |
| LeakAuditor | 泄漏审计，检查敏感信息 |

## 判定规则

### 最终判定 (Verdict)

| 判定 | 条件 |
|------|------|
| PASS | ΔS在SAFE+低风险+所有治理门通过 |
| CONDITIONAL_PASS | ΔS在TRANSIT或治理门COARSE |
| CORRECTED | ΔS在RISK但修正成功 |
| BLOCK | 治理门STOP或CRITICAL失败模式 |
| ESCALATE | ΔS在DANGER或修正失败 |

### ΔS区域 (GateZone)

| 区域 | 范围 | 处理策略 |
|------|------|----------|
| SAFE | 0 - 0.4 | 直接通过 |
| TRANSIT | 0.4 - 0.6 | 有条件通过，监控 |
| RISK | 0.6 - 0.85 | 修正+重评估 |
| DANGER | 0.85+ | 阻断+升级 |

## 数据流

```
输入文本
    │
    ▼
┌────────────────┐
│  Layer 2 检测  │ ──► 规则引擎/幻觉检测
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  Layer 3 推理  │ ──► 七步链/语义防火墙
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  Layer 4 诊断  │ ──► 全局修复/故障排除
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  Layer 5 治理  │ ──► TwinAtlas/7个门
└───────┬────────┘
        │
        ▼
┌────────────────┐
│  Layer 6 执行  │ ──► 目标编译/泄漏审计
└───────┬────────┘
        │
        ▼
    最终判定
```

## 核心流程

### 1. 输入阶段 (Input)

接收AI模型的输出向量与ground truth向量，计算初始阴阳距。

### 2. 阴阳距计算 (DeltaS)

```
delta_s = ||v_output - v_ground_truth||_2
```

根据阈值划分四区：
- SAFE (0-0.4): 安全区域
- TRANSIT (0.4-0.6): 过渡区域
- RISK (0.6-0.85): 风险区域
- DANGER (0.85+): 危险区域

### 3. 坤守修正 (KunGuard)

坤卦象"地"，主承载与修正：
- 计算语义残差
- 判断危害等级
- 执行残差修正
- 知识锚点管理

### 4. 乾进评估 (QianAdvance)

乾卦象"天"，主进取与稳定：
- K路径扰动采样
- 稳定性评分
- 演进趋势预测

### 5. 复归检测 (FuReturn)

复卦象"回归"，主逆转与恢复：
- 状态机转换：NORMAL → WARNING → CRASH → RECOVERING → NORMAL
- 李雅普诺夫指数计算
- 崩溃概率评估
- 自动恢复机制

### 6. 巽调优化 (XunTune)

巽卦象"风"，主调适与柔顺：
- 注意力门控
- 动态权重调节
- 上下文适配

## 16种失败模式

| 编号 | 模式名称 | 描述 | 严重性 |
|------|----------|------|--------|
| 1 | DeltaSpike | 阴阳距突增 | CRITICAL |
| 2 | SemanticDrift | 语义漂移 | HIGH |
| 3 | ModeCollapse | 模式崩塌 | CRITICAL |
| 4 | Hallucination | 幻觉 | HIGH |
| 5 | Contradiction | 自相矛盾 | HIGH |
| 6 | Repetition | 重复循环 | MEDIUM |
| 7 | Truncation | 截断 | LOW |
| 8 | Corruption | 损坏 | CRITICAL |
| 9 | Uncertainty | 不确定 | MEDIUM |
| 10 | Degradation | 退化 | HIGH |
| 11 | LatentSpaceCollapse | 隐空间崩塌 | CRITICAL |
| 12 | AttentionCollapse | 注意力崩塌 | HIGH |
| 13 | GradientExplosion | 梯度爆炸 | CRITICAL |
| 14 | ContextConfusion | 上下文混乱 | MEDIUM |
| 15 | KnowledgeConflict | 知识冲突 | MEDIUM |
| 16 | OutputInstability | 输出不稳定 | HIGH |

## WFGY协议映射

| 协议版本 | 特性 | 状态 |
|----------|------|------|
| WFGY 1.0 | 基础DeltaS计算 | 已实现 |
| WFGY 2.0 | 坤守修正 | 已实现 |
| WFGY 3.0 | 乾进评估 | 已实现 |
| WFGY 4.0 | TwinAtlas + 逆图验证 | 已实现 |
| WFGY 5.0 | 六层架构整合 | 已实现 |

## 配置参数

### VerificationConfig

| 参数 | 默认值 | 描述 |
|------|--------|------|
| delta_threshold | 0.6 | 阴阳距阈值 |
| stability_threshold | 0.7 | 稳定性阈值 |
| hazard_threshold | 0.5 | 危害等级阈值 |
| collapse_threshold | 0.8 | 崩溃阈值 |

### DeltaSCalculator

| 参数 | 默认值 | 描述 |
|------|--------|------|
| metric | 'euclidean' | 距离度量 |
| safe_threshold | 0.4 | 安全阈值 |
| transit_threshold | 0.6 | 过渡阈值 |
| risk_threshold | 0.85 | 风险阈值 |

## 扩展点

### 1. 自定义Embedding Provider

```python
from taiji_verify.embedding import EmbeddingProvider
import numpy as np

class CustomEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> np.ndarray:
        # 实现自定义嵌入逻辑
        return my_embedding_model.encode(text)

    def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        return [self.embed(t) for t in texts]
```

### 2. 自定义治理门

```python
from taiji_verify.governance.governance_gates import (
    GovernanceGate, GateType, GateState, GateResult
)

class CustomGate(GovernanceGate):
    def _custom_evaluation(self, text: str) -> GateResult:
        # 实现自定义评估逻辑
        pass
```

### 3. 自定义规则

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

## 与taiji-agent集成

Taiji Verify 可作为taiji-agent的验证后端：

```python
from taiji_agent import Agent
from taiji_verify.engine import TaijiVerifyEngine

agent = Agent()
verifier = TaijiVerifyEngine()

response = agent.generate(prompt)
verify_result = verifier.verify(
    input_text=response,
    ground_truth=expected_output,
)
```

## 性能考虑

- 向量计算使用NumPy向量化操作
- 状态追踪使用有限队列防止内存泄漏
- 异常检测使用滑动窗口统计
- 治理门评估并行执行

## 未来规划

1. 支持GPU加速向量计算
2. 增加更多距离度量选项
3. 完善时序分析模块
4. 增加可视化监控面板
5. 支持流式验证
