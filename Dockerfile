FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Gunicorn con 1 worker y timeout alto
CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "1", "--threads", "1", "--timeout", "120", "main:app"]
