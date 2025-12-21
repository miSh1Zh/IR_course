FROM python:3.11-slim

WORKDIR /app

# Зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код
COPY medical_crawler /app/medical_crawler
COPY scrapy.cfg /app/
COPY crawl_all.sh /app/
COPY crawl_rotation.sh /app/

# Создать директорию для логов
RUN mkdir -p /app/logs && chmod +x /app/crawl_all.sh /app/crawl_rotation.sh

# Запуск по умолчанию - ротационный режим
CMD ["/app/crawl_rotation.sh"]
