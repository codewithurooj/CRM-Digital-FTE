# Multi-stage Dockerfile for CRM Digital FTE
# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
RUN pip install --no-cache-dir --prefix=/install email-validator

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /install /usr/local

# Copy application code into /app/production/ to match import paths
COPY . ./production/

# Set Python path so "production" package is found
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "production.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
