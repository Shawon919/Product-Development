FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install "uvicorn[standard]" gunicorn

COPY . .

EXPOSE 8000

CMD ["gunicorn", "myproject.asgi:application", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "--reload"]
