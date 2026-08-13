FROM python:3.12-slim

WORKDIR /app

# Install Python deps first (better layer caching), plus gunicorn as the
# production WSGI server (kept out of requirements.txt on purpose so local
# `flask run` / `python app.py` dev workflows are untouched).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

# Copy the rest of the frontend (app.py, templates/, static/)
COPY . .

EXPOSE 5000

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 app:app"]
