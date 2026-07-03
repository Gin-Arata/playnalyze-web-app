# =========================================================
# Dockerfile - Backend Playnalyze (FastAPI + DistilBERT + BART)
# Simpan file ini sebagai: backend/Dockerfile
# Package manager: uv (baca dari pyproject.toml + uv.lock)
# =========================================================

FROM python:3.11-slim

# Ambil binary uv dari image resminya (lebih cepat daripada pip install uv)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Dependency sistem minimal yang sering dibutuhkan torch/transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Layer caching: copy file dependency dulu sebelum source code ---
# Supaya rebuild Docker tidak perlu install ulang dependency kalau cuma kode yang berubah
COPY pyproject.toml uv.lock* ./

# Install dependency (tanpa dev dependency, tanpa install project itu sendiri dulu)
RUN uv sync --frozen --no-install-project --no-dev

# --- PENTING untuk hemat RAM & storage ---
# Jika pyproject.toml Anda memakai "torch" versi default (bawa CUDA/GPU),
# ukurannya bisa 3-5x lebih besar dan boros RAM saat load.
# Kalau tidak pakai GPU di VPS/laptop, ganti dependency torch di pyproject.toml
# menjadi CPU-only, misal dengan menambahkan index berikut di pyproject.toml:
#
# [[tool.uv.index]]
# name = "pytorch-cpu"
# url = "https://download.pytorch.org/whl/cpu"
# explicit = true
#
# [tool.uv.sources]
# torch = { index = "pytorch-cpu" }

# Copy seluruh source code backend
COPY . .

# Install ulang supaya project itu sendiri (kalau ada package lokal) ikut ter-install
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    # Batasi thread agar tidak rebutan CPU core saat inference (aman untuk VPS kecil)
    OMP_NUM_THREADS=2 \
    TOKENIZERS_PARALLELISM=false \
    # Arahkan cache model HuggingFace ke folder yang di-mount sebagai volume
    HF_HOME=/app/.cache/huggingface

EXPOSE 8000

# --workers 1 WAJIB kalau RAM terbatas (tiap worker = duplikat model di memori)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
