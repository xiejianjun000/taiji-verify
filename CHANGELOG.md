# Changelog

所有重要的版本更新将记录在此文件。

## [2.0.0] - 2026-05-16

### 新增功能

#### Phase 1: 覆盖率提升 (75% → 91%)
- symptom_map.py: 72个测试，覆盖率98%
- fu_return.py: 40个测试，覆盖率99%
- polaris.py: 35个测试，覆盖率99%
- qian_advance.py: 30个测试，覆盖率91%
- guan_observe.py: 38个测试，覆盖率94%
- xun_tune.py: 25个测试，覆盖率100%
- engine.py: 37个测试，覆盖率87%

#### Phase 2: inverse_atlas.py 完整实现
- 逆向推理验证逻辑
- 逻辑跳跃检测 (LogicalGap)
- 前提条件推导与验证
- 修复建议生成
- 33个测试用例

#### Phase 3: EmbeddingProvider 抽象层
- `EmbeddingProvider` 抽象基类
- `SimpleBagOfWordsProvider` 零依赖实现
- `OpenAIEmbeddingProvider` OpenAI集成
- `LocalSentenceTransformerProvider` 本地模型支持
- 22个测试用例

#### Phase 4: 端到端集成测试
- 28个端到端场景测试
- 正常场景测试 (环评报告、标准合规)
- 阻断场景测试 (伪造标准、事实矛盾、敏感信息)
- 修正场景测试 (ΔS风险、幻觉检测)
- 逻辑跳跃场景测试
- 崩溃恢复场景测试
- 多层交互测试
- 引擎模式测试
- 压力测试 (顺序、内存、并发)
- 边界条件测试

#### Phase 5: API文档
- 新增 `docs/api.md` 完整API参考文档
- 更新 `docs/architecture.md` 六层架构文档

### 架构改进

#### 六层架构完整实现
1. **Layer 1: 核心层** - ΔS计算、坤守、乾进、复归、巽调、北极星
2. **Layer 2: 检测层** - 规则引擎、幻觉检测、一致性检查、溯源
3. **Layer 3: 推理层** - 七步推理链、语义防火墙、耦合器、检查点
4. **Layer 4: 诊断层** - 全局修复图、故障排除图谱
5. **Layer 5: 治理层** - TwinAtlas、7个治理门
6. **Layer 6: 执行层** - 目标编译器、泄漏审计

#### 7个治理门
- PROBLEM_FORMATION - 问题构成
- WORLD_ALIGNMENT - 世界对齐
- COLLAPSE_GEOMETRY - 崩溃几何
- ADJACENT_CUT - 相邻切割
- RESOLUTION_AUTH - 解决授权
- FIX_LEGALITY - 修复合法性
- EMISSION_CONTROL - Emission控制

### 代码质量
- ruff check: 零错误
- ruff format: 30个文件格式化
- mypy: 基础类型检查通过
- 所有450个测试100%通过

### 统计
- 测试数量: 125 → 450 (+325)
- 覆盖率: 75% → 91% (+16%)
- 源代码行数: ~3000行
- 文档行数: ~1000行

---

## [1.0.0] - 2026-05-15

### 初始版本
- 太极八卦理论核心框架
- 基础DeltaS计算
- 坤守修正模块
- 乾进评估模块
- 复归检测模块
- 巽调优化模块
- 北极星编译器
- 16种失败模式检测
- 基础引擎整合
