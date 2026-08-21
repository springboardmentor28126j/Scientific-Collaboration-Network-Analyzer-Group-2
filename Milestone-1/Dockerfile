# --- Builder stage: resolve and install dependencies with uv ---
FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app

RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python . && \
    uv pip install --python /opt/venv/bin/python "bcrypt==4.0.1"

# --- Runtime stage: slim image, non-root user ---
FROM python:3.12-slim AS runtime

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
