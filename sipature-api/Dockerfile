# SIPATURE inference API (FastAPI).
#
# Build context MUST be the repository root (see sipature-app/docker-compose.yml):
#   docker build -f sipature-api/Dockerfile -t sipature-inference .
#
# PRASYARAT: salin model TF-IDF TERBARU (a10bddb1...) dari Drive ke
# `ml/artifacts/models/tfidf-aspect-silver-v1/` SEBELUM build. Repo lokal
# memuat model lama (9132efbf...); hash diverifikasi saat runtime oleh
# `load_tfidf_contract` terhadap `ml/configs/a9.yaml`, jadi model lama akan gagal.

FROM python:3.10-slim

WORKDIR /app

# Dependency Python (ML + web) lalu package `sipature_ml` editable agar
# `sipature_ml.config.ML_ROOT` tetap menunjuk `/app/ml` (konfigurasi terbaca).
COPY sipature-api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ml /app/ml
RUN pip install --no-cache-dir --no-deps -e /app/ml

# Model TF-IDF (frozen) beserta manifest.
COPY ml/artifacts/models/tfidf-aspect-silver-v1 /app/model

# Aplikasi FastAPI.
COPY sipature-api/app /app/app

ENV MODEL_DIR=/app/model \
    PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
