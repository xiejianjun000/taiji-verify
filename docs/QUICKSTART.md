# Taiji Verify 快速集成指南

**版本**: 2.0.0 | **更新时间**: 2026-05-16

---

## 一、安装

### Python SDK（推荐）

```bash
pip install taiji-verify
```

### Docker（无需Python环境）

```bash
docker run -p 8080:8080 taiji-verify:2.0.0
```

### 或使用docker-compose

```yaml
# docker-compose.yml
services:
  taiji-verify:
    image: taiji-verify:2.0.0
    ports:
      - "8080:8080"
```

```bash
docker-compose up -d
```

---

## 二、Python SDK - 3种使用方式

### 方式1: 一行验证（最简单）

```python
from taiji_verify import verify

result = verify("AI输出文本")
if result.is_passing:
    print("验证通过")
```

### 方式2: 带真值验证

```python
from taiji_verify import verify

result = verify(
    text="AI输出: 碳排放量减少20%",
    ground_truth="碳排放量减少20%",
)
print(f"ΔS: {result.delta_s}")
```

### 方式3: 面向对象（自定义配置）

```python
from taiji_verify import TaijiVerify

verifier = TaijiVerify(
    embedding_dim=768,      # 向量维度
    delta_threshold=0.6,   # ΔS阈值
)

result = verifier.verify("待验证文本")
print(result.details)  # 完整详情
```

---

## 三、HTTP API - 任何语言都能用

### 启动服务

```bash
# Python
uvicorn taiji_verify.api:app --host 0.0.0.0 --port 8080

# 或Docker
docker run -p 8080:8080 taiji-verify:2.0.0
```

### API端点

#### 健康检查

```bash
GET /health
```

响应:
```json
{"status": "healthy", "version": "2.0.0"}
```

#### 单条验证

```bash
POST /verify
Content-Type: application/json

{
    "text": "待验证的AI输出",
    "ground_truth": "标准答案（可选）",
    "context": {"key": "value"}
}
```

响应:
```json
{
    "verdict": "pass",
    "is_passing": true,
    "delta_s": 0.85,
    "risk_level": "SAFE",
    "failures": [],
    "processing_time_ms": 120
}
```

#### 批量验证

```bash
POST /verify/batch
Content-Type: application/json

{
    "texts": ["文本1", "文本2", "文本3"],
    "ground_truths": ["答案1", "答案2", "答案3"],
    "max_workers": 4
}
```

响应:
```json
{
    "results": [...],
    "total": 3,
    "passed": 2,
    "processing_time_ms": 350
}
```

---

## 四、不同语言的HTTP调用示例

### Python

```python
import requests

response = requests.post("http://localhost:8080/verify", json={
    "text": "AI输出文本"
})
result = response.json()
print(result["verdict"])
```

### JavaScript/Node.js

```javascript
const response = await fetch('http://localhost:8080/verify', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({text: 'AI输出文本'})
});
const result = await response.json();
console.log(result.verdict);
```

### Go

```go
data := map[string]string{"text": "AI输出文本"}
jsonData, _ := json.Marshal(data)
resp, _ := http.Post("http://localhost:8080/verify", "application/json", bytes.NewBuffer(jsonData))
```

### Java

```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:8080/verify"))
    .header("Content-Type", "application/json")
    .POST(HttpRequest.BodyPublishers.ofString("{\"text\":\"AI输出文本\"}"))
    .build();
HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
```

### Bash/cURL

```bash
curl -X POST http://localhost:8080/verify \
    -H "Content-Type: application/json" \
    -d '{"text": "AI输出文本"}'
```

---

## 五、CLI命令行工具

```bash
# 安装后可用
pip install taiji-verify

# 单条验证
taiji-verify --text "待验证文本"

# 从文件批量
taiji-verify --batch results.txt

# 从stdin
echo "待验证文本" | taiji-verify --stdin

# JSON输出
taiji-verify --text "文本" --json
```

---

## 六、在其他项目中集成

### 集成到LangChain

```python
from langchain.llms import AIOutputValidator
from taiji_verify import verify

class TaijiValidator:
    def validate(self, text: str) -> bool:
        result = verify(text)
        return result.is_passing

validator = TaijiValidator()
```

### 集成到RAG流水线

```python
from taiji_verify import TaijiVerify

class RAGValidator:
    def __init__(self):
        self.verifier = TaijiVerify()

    def validate_response(self, question: str, answer: str) -> dict:
        result = self.verifier.verify(answer, context={"question": question})
        return {"pass": result.is_passing, "details": result.details}
```

### 集成到CI/CD

```yaml
# .github/workflows/verify.yml
- name: Validate AI Output
  run: |
    taiji-verify --batch output.txt
```

### 集成到FastAPI

```python
from fastapi import FastAPI
from taiji_verify import TaijiVerify

app = FastAPI()
verifier = TaijiVerify()

@app.post("/generate")
async def generate(prompt: str):
    output = await llm.generate(prompt)
    result = verifier.verify(output)
    if not result.is_passing:
        return {"error": "输出未通过验证", "details": result.details}
    return {"output": output}
```

---

## 七、配置参数

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `TAIJI_EMBEDDING_DIM` | 768 | 向量维度 |
| `TAIJI_DELTA_THRESHOLD` | 0.6 | ΔS阈值 |

### SDK配置

```python
verifier = TaijiVerify(
    embedding_dim=768,           # 向量维度
    delta_threshold=0.6,       # ΔS阈值，越低越严格
    enable_all_layers=True,     # 启用全部六层
    enable_governance=True,     # 启用治理层
)
```

---

## 八、判定结果说明

| 判定 | 含义 | 处理建议 |
|------|------|----------|
| `pass` | 通过 | 直接使用 |
| `conditional_pass` | 有条件通过 | 监控使用 |
| `corrected` | 修正后通过 | 检查修正内容 |
| `block` | 阻断 | 不使用，需修复 |
| `escalate` | 升级 | 人工审核 |

---

## 九、失败模式

验证失败时，`failures`字段包含具体原因：

| 模式ID | 名称 | 说明 |
|--------|------|------|
| FM01 | Hallucination | 幻觉检测 |
| FM02 | FactConflict | 事实冲突 |
| FM04 | Overconfidence | 过度自信 |
| FM07 | FormatViolation | 格式违规 |

---

## 十、常见问题

### Q: 误判太多怎么办？

调整`delta_threshold`到0.5或0.4使标准更严格，或0.7更宽松。

### Q: 延迟太高？

使用批量验证`batch_verify`，支持多并发处理。

### Q: 如何自定义规则？

```python
from taiji_verify import TaijiVerify
from taiji_verify.detection.rule_engine import Rule, RuleEngine

class CustomRule(Rule):
    id = "custom_001"
    name = "自定义规则"
    pattern = r"特定模式"
    severity = "HIGH"

verifier = TaijiVerify()
# 添加自定义规则到规则引擎
```

---

## 十一、技术支持

- 文档: [docs/](docs/)
- 架构: [docs/architecture.md](docs/architecture.md)
- API: [docs/api.md](docs/api.md)
