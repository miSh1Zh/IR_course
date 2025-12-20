FROM python:3.11-slim

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY medical_crawler /app/medical_crawler
COPY scrapy.cfg /app/

# Создать директорию для логов
RUN mkdir -p /app/logs

# Запуск краулера (можно переопределить)
CMD ["scrapy", "crawl", "journaldoctor", "-L", "INFO"]

