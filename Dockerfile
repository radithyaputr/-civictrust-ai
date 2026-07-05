# =============================================================================
# CivicTrust AI - Production Dockerfile (Multi-stage)
# =============================================================================
# Build:
#   docker build -t civictrust-ai .
#
# Run backend:
#   docker run -p 8000:8000 civictrust-ai backend
#
# Run frontend:
#   docker run -p 8501:8501 civictrust-ai frontend
#
# Run both (requires docker compose):
#   docker-compose up -d
# =============================================================================

# ---- Build Stage ----
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---- Runtime Stage ----
FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY app/ app/
COPY scripts/ scripts/
COPY data/ data/
COPY frontend/ frontend/
COPY .streamlit/ .streamlit/
COPY .env.example .env.example
COPY LICENSE .

EXPOSE 8000 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# ---- Backend ----
FROM runtime AS backend

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

# ---- Frontend ----
FROM runtime AS frontend

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
