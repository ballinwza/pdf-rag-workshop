# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/wheels /workspace/wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /workspace/wheels/*

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000 8501

CMD ["./entrypoint.sh"]