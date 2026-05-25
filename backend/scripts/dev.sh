#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Checking database connection..."
until pg_isready -h localhost -p 5432 -U lumen >/dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
uvicorn app.main:app --reload