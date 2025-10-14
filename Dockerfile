# Base image
FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV DJANGO_SETTINGS_MODULE=myproject.settings.production

WORKDIR /app

# Install OS dependencies for PostgreSQL, cryptography, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Production command
CMD ["gunicorn", "myproject.asgi:application", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]
