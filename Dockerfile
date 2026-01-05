## Multi-stage Dockerfile: build dependencies then produce a slim runtime image
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install build deps for compiling any wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r /app/requirements.txt

# Copy source
COPY . /app

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy installed packages and app from builder
COPY --from=builder /install /usr/local
COPY --from=builder /app /app

# Ensure log dir exists
RUN mkdir -p /app/log

EXPOSE 5001

# Use Gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app:app", "--workers=2"]
