# =========================================================
# Dockerfile - Backend Playnalyze (FastAPI + DistilBERT + BART)
# Versi optimasi: multi-stage build + torch CPU-only
# =========================================================

# ---------- STAGE 1: builder ----------
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy file dependency dulu supaya layer cache tetap efektif
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev

# Baru copy source code, lalu install project itu sendiri
COPY . .
RUN uv sync --frozen --no-dev

# ---------- STAGE 2: runtime (image final, tanpa build tools) ----------
FROM python:3.13-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Hanya copy hasil venv + source code, TIDAK ada build-essential, uv cache, dsb
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=2 \
    TOKENIZERS_PARALLELISM=false \
    HF_HOME=/app/.cache/huggingface

EXPOSE 8000

# --workers 1 WAJIB kalau RAM terbatas (tiap worker = duplikat model di memori)
CMD ["python", "main.py"]