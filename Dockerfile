# --- Base ---
FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONPATH=/app/src
RUN pip install --no-cache-dir six poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root
ENV PATH="/app/.venv/bin:$PATH"

# --- Development ---
FROM base AS development
COPY . .

# --- Production ---
FROM base AS production
RUN poetry install --no-root --only main
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini ./
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
