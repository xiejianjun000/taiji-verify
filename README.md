# Taiji Verify - 太极验证引擎

基于八卦理论的AI输出语义验证系统，通过六层架构实现对AI输出语义漂移的实时监控与修正。

**版本: 2.0.0** | **测试: 450** | **覆盖率: 91%**

## 核心模块

| 模块 | 八卦 | 功能 |
|------|------|------|
| DeltaS | 阴阳 | 阴阳距计算 - 量化输出与真值的语义距离 |
| KunGuard | 坤 | 坤守修正 - 语义残差修正，锚定知识边界 |
| QianAdvance | 乾 | 乾进评估 - 语义演进建模，评估稳定性 |
| FuReturn | 复 | 复归检测 - 崩溃逆转，恢复正常状态 |
| XunTune | 巽 | 巽调优化 - 注意力调节，动态门控 |
| Polaris | 北辰 | 北辰编译器 - 任务分解与执行调度 |
| TwinAtlas | 双图 | 正向路由 + 逆向验证 |
| Engine | 引擎 | 六层验证主引擎 |

## 六层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Layer 6: 执行层                           │
│              目标编译器(Polaris) | 泄漏审计(LeakAuditor)           │
├─────────────────────────────────────────────────────────────────┤
│                        Layer 5: 治理层                           │
│   TwinAtlas | 7个治理门(PROBLEM_FORMATION/WORLD_ALIGNMENT等)      │
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

## 安装

```bash
pip install -e .
```

或安装开发依赖：

```bash
pip install -e ".[dev]"
```

## 快速开始

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

### 向量验证

```python
import numpy as np
from taiji_verify.engine import TaijiVerifyEngine

engine = TaijiVerifyEngine()

input_vec = np.random.randn(768)
ground_vec = np.random.randn(768)

response = engine.verify_with_vectors(input_vec, ground_vec)
print(f"判定: {response.verdict}")
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

## 判定结果

| 判定 | 说明 |
|------|------|
| PASS | 通过 - ΔS在SAFE+低风险+所有治理门通过 |
| CONDITIONAL_PASS | 有条件通过 - ΔS在TRANSIT或治理门COARSE |
| CORRECTED | 修正后通过 - ΔS在RISK但修正成功 |
| BLOCK | 阻断 - 治理门STOP或CRITICAL失败模式 |
| ESCALATE | 升级 - ΔS在DANGER或修正失败 |

## ΔS区域

| 区域 | 范围 | 处理策略 |
|------|------|----------|
| SAFE | 0 - 0.4 | 直接通过 |
| TRANSIT | 0.4 - 0.6 | 有条件通过，监控 |
| RISK | 0.6 - 0.85 | 修正+重评估 |
| DANGER | 0.85+ | 阻断+升级 |

## 7个治理门

| 门类型 | 描述 | 输出状态 |
|--------|------|----------|
| PROBLEM_FORMATION | 问题是否有效形成 | STOP/COARSE/AUTHORIZED |
| WORLD_ALIGNMENT | 是否与已知事实对齐 | STOP/AUTHORIZED |
| COLLAPSE_GEOMETRY | 是否有崩溃迹象 | STOP/COARSE/AUTHORIZED |
| ADJACENT_CUT | 是否与相邻领域冲突 | COARSE/AUTHORIZED |
| RESOLUTION_AUTH | 是否赢得存在权利 | COARSE/UNRESOLVED/AUTHORIZED |
| FIX_LEGALITY | 修正是否合法 | STOP/AUTHORIZED |
| EMISSION_CONTROL | 是否可公开发布 | STOP/AUTHORIZED |

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行覆盖率
pytest tests/ --cov=src/taiji_verify --cov-report=html

# 代码质量检查
ruff check src/
ruff format src/
mypy src/ --ignore-missing-imports
```

## 项目结构

```
taiji-verify/
├── src/taiji_verify/      # 核心模块
│   ├── delta_s.py          # 阴阳距
│   ├── kun_guard.py        # 坤守
│   ├── qian_advance.py     # 乾进
│   ├── fu_return.py        # 复归
│   ├── xun_tune.py         # 巽调
│   ├── guan_observe.py     # 观变
│   ├── polaris.py          # 北辰编译器
│   ├── engine.py           # 主引擎
│   ├── embedding.py         # Embedding提供者
│   ├── detection/          # 检测层
│   ├── reasoning/          # 推理层
│   ├── diagnosis/          # 诊断层
│   ├── governance/         # 治理层
│   └── execution/          # 执行层
├── tests/                  # 测试套件 (450个测试)
├── docs/                   # 文档
│   ├── architecture.md     # 架构说明
│   └── api.md              # API参考
├── CHANGELOG.md           # 更新日志
└── pyproject.toml         # 项目配置
```

## 文档

- [架构文档](docs/architecture.md) - 六层架构详解
- [API参考](docs/api.md) - 完整接口文档

## 许可

MIT License - 详见 LICENSE 文件
