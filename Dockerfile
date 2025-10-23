FROM python:3.11-bullseye AS builder

RUN pip install --no-cache-dir uv

WORKDIR /opt/app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY src/ ./src/

#-----------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /opt/app

RUN useradd --system --no-create-home --shell /bin/false --home /nonexistent appuser

COPY --from=builder --chown=appuser:appuser /opt/app/.venv /opt/app/.venv
COPY --from=builder --chown=appuser:appuser /opt/app/src /opt/app/

USER appuser

ENV PATH="/opt/app/.venv/bin:$PATH" \
    PYTHONPATH="/opt/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["python", "main.py"]
