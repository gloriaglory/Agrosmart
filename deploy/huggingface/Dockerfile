# Hugging Face Space for the AgroSmart backend.
# The Space holds only this file and README.md; the code is cloned from GitHub
# (with its Git LFS models) when the Space builds. To deploy a new version, use
# Space Settings -> "Factory rebuild".
FROM python:3.11-slim

ARG REPO=https://github.com/gloriaglory/Agrosmart.git
ARG BRANCH=main

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_CPP_MIN_LOG_LEVEL=2 \
    WEB_PORT=7860 \
    HOME=/home/app

# git + git-lfs to fetch the code and models; libgomp1 for LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends git git-lfs libgomp1 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 app

# Only the backend's LFS files (models), not the website's video
RUN GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --branch "$BRANCH" "$REPO" /src \
    && cd /src && git lfs install --local && git lfs pull --include "crop_recommendation/**" \
    && rm -rf /src/.git /src/Web /src/ml

WORKDIR /src/crop_recommendation
# tensorflow-cpu is the same TensorFlow without GPU libraries (about 1 GB smaller)
RUN sed 's/^tensorflow==/tensorflow-cpu==/' requirements.txt > /tmp/requirements.txt \
    && pip install -r /tmp/requirements.txt \
    && SECRET_KEY=build-only python manage.py collectstatic --noinput >/dev/null \
    && chown -R app:app /src

USER app
EXPOSE 7860
CMD ["./entrypoint.sh"]
