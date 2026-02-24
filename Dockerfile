# Auth Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first
COPY fiap-soat-video-shared/ /tmp/video-processor-shared/
RUN pip install --no-cache-dir /tmp/video-processor-shared/

# Copy requirements and install dependencies
COPY fiap-soat-video-auth/pyproject.toml .
RUN pip install --no-cache-dir \
    "fastapi>=0.109.0" \
    "uvicorn[standard]>=0.27.0" \
    "prometheus-client>=0.20.0" \
    "pydantic>=2.0.0" \
    "pydantic-settings>=2.0.0" \
    "pydantic[email]>=2.0.0" \
    "sqlalchemy>=2.0.0" \
    "asyncpg>=0.29.0" \
    "psycopg2-binary>=2.9.0" \
    "redis>=5.0.0" \
    "python-multipart>=0.0.6"

# Copy application code
COPY fiap-soat-video-auth/src/ src/

# Set Python path
ENV PYTHONPATH=/app/src

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "auth_service.infrastructure.adapters.input.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
