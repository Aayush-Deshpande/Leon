# Leon backend — single-instance demo image ([500], A-8).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY app ./app

# Binds 0.0.0.0 inside the container; host exposure is restricted to 127.0.0.1
# via compose port mapping (honors [310] SEC-1 — no public bind).
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
