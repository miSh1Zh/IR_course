FROM gcc:12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    make \
    && rm -rf /var/lib/apt/lists/*

# Копировать код
COPY src /app/src
COPY Makefile /app/

# Собрать
RUN make all

# Том для данных
VOLUME ["/app/data"]

# По умолчанию запускать searcher
CMD ["./searcher"]

