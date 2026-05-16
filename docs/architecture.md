# Taiji Verify 架构说明

## 设计理念

太极验证引擎源自中国古代哲学"太极生两仪，两仪生四象，四象生八卦"的思想，将AI语义验证过程映射为八卦运转：

- **阴阳 (Yin-Yang)**: 输入与输出的对立统一
- **八卦 (Bagua)**: 八种验证状态与修正策略

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
- 状态机转换
- 崩溃概率评估
- 自动恢复机制

### 6. 巽调优化 (XunTune)

巽卦象"风"，主调适与柔顺：
- 注意力门控
- 动态权重调节
- 上下文适配

### 7. 引擎整合 (Engine)

```
Input → DeltaS → KunGuard → QianAdvance → FuReturn → XunTune → Output
```

## 16种失败模式

| 编号 | 模式名称 | 描述 |
|------|----------|------|
| 1 | Delta Spike | 阴阳距突增 |
| 2 | Semantic Drift | 语义漂移 |
| 3 | Mode Collapse | 模式崩塌 |
| 4 | Hallucination | 幻觉 |
| 5 | Contradiction | 自相矛盾 |
| 6 | Repetition | 重复循环 |
| 7 | Truncation | 截断 |
| 8 | Corruption | 损坏 |
| 9 | Uncertainty | 不确定 |
| 10 | Degradation | 退化 |
| 11 | Latent Space Collapse | 隐空间崩塌 |
| 12 | Attention Collapse | 注意力崩塌 |
| 13 | Gradient Explosion | 梯度爆炸 |
| 14 | Context Confusion | 上下文混乱 |
| 15 | Knowledge Conflict | 知识冲突 |
| 16 | Output Instability | 输出不稳定 |

## 数据流

```
                    ┌─────────────┐
                    │   Context   │
                    └──────┬──────┘
                           │
                           ▼
┌──────────┐    ┌─────────────┐    ┌──────────────┐
│  Ground  │───▶│   DeltaS    │───▶│  KunGuard    │
│  Truth   │    │  (阴阳距)   │    │   (坤守)     │
└──────────┘    └─────────────┘    └──────┬───────┘
                                          │
                                          ▼
┌──────────┐    ┌─────────────┐    ┌──────────────┐
│ Output   │───▶│ QianAdvance │◀───│  FuReturn    │
│  Vector  │    │   (乾进)   │    │    (复归)    │
└──────────┘    └──────┬──────┘    └──────────────┘
                        │
                        ▼
                ┌─────────────┐
                │  XunTune    │
                │   (巽调)   │
                └──────┬──────┘
                        │
                        ▼
                ┌─────────────┐
                │   Engine    │
                │  (验证结果) │
                └─────────────┘
```

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

### 1. 自定义距离度量

```python
from taiji_verify.delta_s import DeltaSCalculator

class CosineDeltaS(DeltaSCalculator):
    def _compute_distance(self, v1, v2):
        return 1 - np.dot(v1, v2)
```

### 2. 自定义失败模式

```python
from taiji_verify.symptom_map import SymptomMap, FailureSymptom

symptom_map = SymptomMap()
symptom_map.register_custom_pattern(my_pattern)
```

### 3. 插件集成

```python
# contrib/plugins.py 提供了可选的插件系统
from taiji_verify.contrib.plugins import TaijiPlugin

class MyPlugin(TaijiPlugin):
    name = "my-plugin"
    def on_verify(self, state):
        # 自定义处理
        pass
```

## 性能考虑

- 向量计算使用NumPy向量化操作
- 状态追踪使用有限队列防止内存泄漏
- 异常检测使用滑动窗口统计

## 未来规划

1. 支持GPU加速
2. 增加更多距离度量选项
3. 完善时序分析模块
4. 增加可视化监控面板
