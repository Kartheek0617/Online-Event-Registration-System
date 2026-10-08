# Multi-stage secure Dockerfile for Backend Service
# Follows CIS Benchmark and OWASP Container Security Guidelines

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create an isolated Python virtual environment
RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt .

# Install Python dependencies into the virtual environment
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Final minimal runtime stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Install runtime PostgreSQL libraries and curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy isolated Python environment from builder
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root unprivileged service account
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -d /app appuser

# Copy application source code
COPY backend /app/backend

RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER 10001:10001

# Render supplies PORT at runtime
EXPOSE 8000

# Health check

# Start FastAPI using Render's PORT, with 8000 as local fallback
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]