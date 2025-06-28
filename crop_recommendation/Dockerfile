# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.9.0
# FROM python:${PYTHON_VERSION}-slim as base
FROM python:3.10-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1


WORKDIR /app

# Install required library for joblib/OpenMP support
RUN apt-get update && apt-get install -y libgomp1


# Create directory structure for ML model files
RUN mkdir -p /app/ml_model/crop /app/disease_detection/ml_models

# Copy model files
# Note: These files must exist in your build context
# If they're in your local project, make sure to include them when building the Docker image
RUN pwd
COPY ./crop_predictor/ml_models/crop/ /app/ml_model/crop/
COPY ./disease_detection/ml_models/ /app/disease_detection/ml_models/
RUN pwd
# COPY ./ml_model_files/scaler.joblib /app/ml_model/crop/

# Check if the model files exist
RUN if [ ! -f /app/ml_model/crop/crop_recomendation.joblib ] || [ ! -f /app/ml_model/crop/scaler.joblib ]; then \
    echo "Error: Crop model files not found. Ensure they exist in your build context."; \
    exit 1; \
    fi && \
    if [ ! -f /app/disease_detection/ml_models/plant_disease_model.keras ]; then \
    echo "Error: Disease detection model file not found. Ensure it exists in your build context."; \
    exit 1; \
    fi


# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt
RUN pip install cryptography

# Add path for the AI model
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R "${UID}":"${UID}" /app
# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .


# Expose the port that the application listens on.
EXPOSE 8000


# Run the application.
# Command to run migrations and start the server
CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput || echo "Collectstatic failed" && \
    gunicorn crop_recommendation.wsgi --bind=0.0.0.0:8000
