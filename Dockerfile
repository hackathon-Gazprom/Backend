FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt entrypoint.sh ./


RUN pip install -r requirements.txt --no-cache-dir && pip install gunicorn==21.2.0

COPY src/backend .

CMD ["sh", "entrypoint.sh"]