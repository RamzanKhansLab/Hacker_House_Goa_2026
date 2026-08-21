FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /service

# Copy dependency files first
COPY requirements.txt ./
COPY pyproject.toml ./

# Install normal + ML dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e ".[ml]"

# Copy application source after dependencies
COPY . ./

# Create non-root user
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /service

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]