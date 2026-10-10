FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # FIX #1: Set PYTHONPATH agar `python -m gmgn_bot` bisa menemukan modul
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# FIX #2: Buat direktori /data lebih awal agar tidak crash
# saat Railway Volume belum di-mount atau saat pertama kali dijalankan
RUN mkdir -p /data

# Layer cache: instal dependensi dulu, kode belakangan.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

CMD ["python", "-m", "gmgn_bot"]
