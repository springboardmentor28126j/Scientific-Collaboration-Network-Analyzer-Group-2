#!/bin/bash
set -e

cd backend

echo "Running database migrations..."
alembic upgrade head || echo "Migration warning - continuing startup"

echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
