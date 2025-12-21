FROM python:3.11-slim

WORKDIR /app

# Установить компилятор для сборки C++ searcher
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Python зависимости
COPY ./web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать C++ исходники и собрать searcher
COPY ./engine/src /app/engine/src
COPY ./engine/Makefile /app/engine/
RUN cd /app/engine && make searcher

# Flask приложение
COPY ./web/app.py /app/
COPY ./web/templates /app/templates

EXPOSE 5000

ENV SEARCHER_PATH=/app/engine/searcher
ENV INDEX_PATH=/app/data/index.bin

CMD ["python", "app.py"]
