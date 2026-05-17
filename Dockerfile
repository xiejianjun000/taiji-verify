FROM python:3.11-slim

LABEL maintainer="Junge <awep000@qq.com>"
LABEL description="Taiji Verify - 太极验证引擎 API服务"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

EXPOSE 8080

ENV TAIJI_EMBEDDING_DIM=768
ENV TAIJI_DELTA_THRESHOLD=0.6

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "taiji_verify.api:app", "--host", "0.0.0.0", "--port", "8080"]
