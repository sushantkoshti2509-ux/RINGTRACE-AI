# ==============================================================================
# Multi-Stage Production Dockerfile for RINGTRACE AI
# Stage 1: Compile React Frontend
# Stage 2: Python 3.12 Slim Unified Production Server (FastAPI + React SPA)
# ==============================================================================

# ----------------- Stage 1: Frontend Build -----------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ----------------- Stage 2: Production Server -----------------
FROM python:3.12-slim AS runner

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code, models, configurations, and reference data
COPY config.py .
COPY run_pipeline.py .
COPY src/ ./src/
COPY data/ ./data/
COPY models/ ./models/
COPY reports/ ./reports/

# Copy compiled React SPA assets from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MPLCONFIGDIR=/tmp/matplotlib_cache \
    OMP_NUM_THREADS=1 \
    PORT=8000 \
    HOST=0.0.0.0

EXPOSE 8000

# Health check to ensure API is responsive
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Launch production server with dynamic port binding
CMD ["sh", "-c", "uvicorn src.integration.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
