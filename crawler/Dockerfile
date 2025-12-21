FROM python:3.11-slim

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY medical_crawler /app/medical_crawler
COPY scrapy.cfg /app/
COPY crawl_all.sh /app/

# Создать директорию для логов
RUN mkdir -p /app/logs && chmod +x /app/crawl_all.sh

# Запуск всех spider'ов
CMD ["/app/crawl_all.sh"]
