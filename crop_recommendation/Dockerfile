# AgroSmart backend image. Build from this folder after `git lfs pull`:
#   docker build -t agrosmart-api .
#   docker run -p 7860:7860 --env-file .env agrosmart-api
# Hugging Face Spaces builds it with deploy/huggingface/Dockerfile instead.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    WEB_PORT=7860 \
    HOME=/home/app

# libgomp1: OpenMP runtime needed by LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app

WORKDIR /app
COPY requirements.txt .
# tensorflow-cpu is the same TensorFlow without GPU libraries (about 1 GB smaller)
RUN sed 's/^tensorflow==/tensorflow-cpu==/' requirements.txt > /tmp/requirements.txt \
    && pip install -r /tmp/requirements.txt

COPY . .
# The app user must be able to write here (SQLite database, local uploads)
RUN SECRET_KEY=build-only python manage.py collectstatic --noinput >/dev/null \
    && chown -R app:app /app

USER app
EXPOSE 7860
CMD ["./entrypoint.sh"]
