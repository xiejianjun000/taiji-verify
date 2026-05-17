# Taiji Verify 插件化集成指南

**版本**: 2.0 | **更新**: 2026-05-16

---

## 一、概述

Taiji Verify 可作为插件集成到其他AI Agent项目中，提供AI输出语义验证能力。

### 支持的集成方式

| 目标项目 | 技术栈 | 集成方式 |
|----------|--------|----------|
| **Hermes Agent** | Python | 直接import SDK |
| **OpenClaw** | Node.js | HTTP API |
| **其他项目** | 任意 | HTTP API |

---

## 二、集成到 Hermes Agent

### 方式1: 作为Skill使用

1. **安装依赖**
```bash
pip install taiji-verify
```

2. **创建Skill文件**
```bash
# 在Hermes skills目录创建
mkdir -p ~/.hermes/skills
cp taiji_verify_skill.py ~/.hermes/skills/
```

3. **使用**
```
/taiji-verify 碳排放量减少了20%
```

### 方式2: 在代码中调用

```python
from taiji_verify import verify

# 验证回答
result = verify("AI输出文本")
if not result.is_passing:
    print(f"检测到问题: {result.failures}")
```

### 方式3: 作为Tool函数

```python
from taiji_verify import TaijiVerify

verifier = TaijiVerify()

# 在Agent执行循环中调用
def agent_step(input_text: str) -> str:
    response = llm.generate(input_text)

    # 验证输出
    result = verifier.verify(response)
    if not result.is_passing:
        # 触发修正或重新生成
        return regenerate(response)

    return response
```

---

## 三、集成到 OpenClaw

### 方式1: 使用HTTP API

OpenClaw通过HTTP调用外部服务进行验证。

1. **启动Taiji Verify API服务**
```bash
# Python
uvicorn taiji_verify.api:app --port 8080

# 或Docker
docker run -p 8080:8080 taiji-verify:2.0.0
```

2. **配置OpenClaw Skill**

在 `~/.openclaw/config.yaml` 中添加:
```yaml
skills:
  - name: taiji-verify
    type: http
    config:
      url: http://localhost:8080/verify
      method: POST
      triggers:
        - /verify
        - /验证
```

### 方式2: 使用官方Skill包

```bash
npm install @your-org/openclaw-skill-taiji-verify
```

配置:
```javascript
// ~/.openclaw/skills/taiji-verify.js
const { taijiVerifySkill } = require('@your-org/openclaw-skill-taiji-verify');

module.exports = {
  skills: [taijiVerifySkill]
};
```

### 方式3: 在OpenClaw插件中调用

```typescript
// extensions/taiji-verify.ts
import { taijiVerifySkill } from '@your-org/openclaw-skill-taiji-verify';

export default {
  skills: [taijiVerifySkill]
};
```

---

## 四、集成到任意项目

### HTTP API调用

Taiji Verify提供REST API，任何语言都可以调用:

```bash
# 健康检查
curl http://localhost:8080/health

# 单条验证
curl -X POST http://localhost:8080/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "待验证文本"}'

# 批量验证
curl -X POST http://localhost:8080/verify/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["文本1", "文本2"]}'
```

### Python SDK直接集成

```python
from taiji_verify import verify, TaijiVerify

# 方式1: 一行验证
result = verify("文本")

# 方式2: 面向对象
verifier = TaijiVerify(
    embedding_dim=768,
    delta_threshold=0.6,
)
result = verifier.verify("文本", ground_truth="标准答案")
```

---

## 五、架构示意图

```
┌─────────────────────────────────────────────────────────────────┐
│                        其他AI Agent项目                           │
├─────────────────────────────────────────────────────────────────┤
│  Hermes Agent  ──────►  import taiji_verify  ──────►  SDK调用  │
│  OpenClaw     ──────►  HTTP API调用         ──────►  REST     │
│  其他项目      ──────►  HTTP/SDK              ──────►  任选    │
├─────────────────────────────────────────────────────────────────┤
│                    Taiji Verify 服务                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Python SDK │  │  HTTP API   │  │  CLI工具    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                    六层验证架构                                   │
│  Core → Detection → Reasoning → Diagnosis → Governance → Execution │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、配置参数

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TAIJI_EMBEDDING_DIM` | 768 | 向量维度 |
| `TAIJI_DELTA_THRESHOLD` | 0.6 | ΔS阈值 |

### SDK配置

```python
TaijiVerify(
    embedding_dim=768,           # 向量维度
    delta_threshold=0.6,         # ΔS阈值，越低越严格
    enable_all_layers=True,      # 启用全部六层
    enable_governance=True,      # 启用治理层
)
```

### API配置

```yaml
# docker-compose.yml
environment:
  - TAIJI_EMBEDDING_DIM=768
  - TAIJI_DELTA_THRESHOLD=0.6
```

---

## 七、判定结果使用

| 判定 | Agent应该如何处理 |
|------|-------------------|
| `pass` | 直接使用输出 |
| `conditional_pass` | 监控使用，可接受 |
| `corrected` | 检查修正内容，确认后使用 |
| `block` | 不使用，要求重新生成 |
| `escalate` | 人工审核 |

### 代码示例

```python
from taiji_verify import verify, Verdict

result = verify(agent_output)

if result.verdict == Verdict.BLOCK:
    # 阻断：输出不可用
    raise ValueError(f"输出被阻断: {result.failures}")

elif result.verdict == Verdict.ESCALATE:
    # 升级：需要人工审核
    send_to_human_review(result)

elif result.verdict == Verdict.CORRECTED:
    # 修正：使用修正后的输出
    output = result.corrected_text or agent_output
    log_correction(result)

else:
    # 通过或有条件通过
    pass
```

---

## 八、部署方式

### 选项1: 嵌入式（推荐小规模）

直接pip安装，SDK在应用内运行。

```bash
pip install taiji-verify
```

### 选项2: 独立服务（推荐大规模）

独立部署API服务，多个Agent共享。

```bash
# Docker
docker run -d -p 8080:8080 taiji-verify:2.0.0

# Kubernetes
kubectl apply -f taiji-verify-deployment.yaml
```

### 选项3: 无服务器

使用Serverless函数部署API。

```yaml
# serverless.yml
functions:
  verify:
    handler: handler.verify
    events:
      - http:
          path: /verify
          method: post
```

---

## 九、文件清单

| 文件 | 说明 |
|------|------|
| `contrib/hermes/taiji_verify_skill.py` | Hermes Agent Skill |
| `contrib/openclaw/taiji-verify-skill/` | OpenClaw Skill包 |
| `src/taiji_verify/plugin.py` | SDK简化接口 |
| `src/taiji_verify/api.py` | FastAPI服务 |
| `src/taiji_verify/cli.py` | CLI工具 |
| `Dockerfile` | Docker镜像 |
| `docker-compose.yml` | Docker Compose |

---

## 十、常见问题

### Q: 如何选择嵌入模型?

A: Taiji Verify默认使用词袋模型(零依赖)。对于更精确的语义匹配，可以配置:
- OpenAI: `OpenAIEmbeddingProvider`
- 本地: `LocalSentenceTransformerProvider`

### Q: 延迟太高怎么办?

A: 使用批量验证`batch_verify()`，支持多并发处理。或者部署独立API服务进行水平扩展。

### Q: 如何自定义验证规则?

A: 通过RuleEngine添加自定义规则:
```python
from taiji_verify.detection.rule_engine import Rule

rule = Rule(
    id="custom_001",
    pattern=r"特定模式",
    severity="HIGH",
)
engine.add_rule(rule)
```
