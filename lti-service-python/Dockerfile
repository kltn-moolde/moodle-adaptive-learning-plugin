# Dockerfile for LTI Service Python
FROM python:3.11-slim

WORKDIR /app

# 🧩 Fix missing sources.list (use fast mirror)
RUN echo "deb http://mirror.sjtu.edu.cn/debian bookworm main contrib non-free non-free-firmware\n\
deb http://mirror.sjtu.edu.cn/debian bookworm-updates main contrib non-free non-free-firmware\n\
deb http://mirror.sjtu.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware" \
> /etc/apt/sources.list

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8082

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8082/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8082"]