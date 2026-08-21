FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /service

# Required to compile hnswlib and other native Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency files first
COPY requirements.txt ./
COPY pyproject.toml ./

# Upgrade packaging tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install application + ML dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e ".[ml]"

# Copy application
COPY . ./

# Create non-root user
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /service

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]