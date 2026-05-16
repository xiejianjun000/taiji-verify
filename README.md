# Taiji Verify - 太极验证引擎

基于八卦理论的AI输出语义验证系统，通过"阴阳距计算"、"坤守修正"、"乾进评估"、"复归检测"、"巽调优化"五模块联动，实现对AI输出语义漂移的实时监控与修正。

## 核心模块

| 模块 | 八卦 | 功能 |
|------|------|------|
| DeltaS | 阴阳 | 阴阳距计算 - 量化输出与真值的语义距离 |
| KunGuard | 坤 | 坤守修正 - 语义残差修正，锚定知识边界 |
| QianAdvance | 乾 | 乾进评估 - 语义演进建模，评估稳定性 |
| FuReturn | 复 | 复归检测 - 崩溃逆转，恢复正常状态 |
| XunTune | 巽 | 巽调优化 - 注意力调节，动态门控 |
| Polaris | 北辰 | 北辰编译器 - 任务分解与执行调度 |
| SymptomMap | 病候 | 16种失败模式检测 - 全面覆盖异常场景 |
| Engine | 引擎 | 太极验证主引擎 - 整合五大模块的验证流水线 |

## 架构图

```
                    输入向量
                        │
                        ▼
                ┌───────────────┐
                │   DeltaS      │ ← 阴阳距计算
                │  阴阳模块     │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │  KunGuard     │ ← 残差修正
                │   坤守        │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ QianAdvance   │ ← 稳定性评估
                │   乾进        │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │  FuReturn     │ ← 崩溃逆转
                │   复归        │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │   XunTune    │ ← 注意力调节
                │   巽调        │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │    Engine     │ ← 验证结果
                │ 太极验证引擎  │
                └───────────────┘
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

```python
from taiji_verify import TaijiVerifyEngine, InputState
import numpy as np

# 初始化引擎
engine = TaijiVerifyEngine()

# 准备输入
input_state = InputState(
    output_vector=np.random.randn(128).astype(np.float32),
    ground_truth_vector=np.random.randn(128).astype(np.float32),
    context={'task': 'reasoning'}
)

# 执行验证
result = engine.verify(input_state)

# 检查结果
if result.overall_safe:
    print("✓ 验证通过")
else:
    print(f"✗ 检测到问题: {result.detected_patterns}")
```

## 各模块详解

### DeltaS (阴阳距)

```python
from taiji_verify.delta_s import DeltaSCalculator, GateZone

calc = DeltaSCalculator()
result = calc.compute(output_vec, ground_truth_vec)

print(f"阴阳距: {result.delta_s:.4f}")
print(f"区域: {result.zone.name}")
print(f"安全: {result.is_safe}")
```

### KunGuard (坤守)

```python
from taiji_verify.kun_guard import KunGuard, HazardLevel

guard = KunGuard()
residual = guard.compute_residual(output_vec, ground_vec)
level, needs_correction = guard.check_hazard(residual)

if needs_correction:
    corrected = guard.correct(output_vec, ground_vec)
```

### SymptomMap (病候图)

```python
from taiji_verify.symptom_map import SymptomMap, SymptomType

symptom_map = SymptomMap()
symptom = symptom_map.detect(state)
print(f"检测到症状: {symptom.symptom_type.name}")
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行覆盖率
pytest tests/ --cov=taiji_verify --cov-report=html
```

## 项目结构

```
taiji-verify/
├── src/taiji_verify/      # 核心模块
│   ├── delta_s.py         # 阴阳距
│   ├── kun_guard.py       # 坤守
│   ├── qian_advance.py    # 乾进
│   ├── fu_return.py       # 复归
│   ├── xun_tune.py        # 巽调
│   ├── guan_observe.py    # 观变
│   ├── polaris.py         # 北辰编译器
│   ├── symptom_map.py     # 病候图
│   ├── engine.py          # 主引擎
│   └── failure_modes.py   # 失败模式
├── tests/                  # 测试套件
├── contrib/                # 可选集成
│   └── plugins.py         # 插件系统（可选）
└── docs/                  # 文档
    └── architecture.md    # 架构说明
```

## 许可

MIT License - 详见 LICENSE 文件
