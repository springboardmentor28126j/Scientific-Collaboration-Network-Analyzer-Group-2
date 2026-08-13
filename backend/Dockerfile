FROM python:3.12-slim

# System deps needed to build psycopg[binary]/bcrypt wheels on some platforms
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend (app code, alembic migrations, alembic.ini)
COPY . .

# Uploaded files (e.g. conference presentations) live here; mounted as a volume in compose
RUN mkdir -p uploads/conference_presentations

EXPOSE 8000

# Run pending Alembic migrations, then start the API.
# Binds to $PORT if set (Render injects this dynamically); falls back to 8000
# for local docker-compose, which doesn't set PORT.
# If DATABASE_URL is unreachable this will fail fast and the container will exit,
# which is the correct behavior (fail loud, don't serve against a stale schema).
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
