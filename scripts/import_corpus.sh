#!/bin/bash
set -e

cd "$(dirname "$0")/.."

if [ -z "$1" ]; then
    echo "Использование: ./scripts/import_corpus.sh <файл.json или файл.json.gz>"
    exit 1
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
    echo "Ошибка: файл не найден: $INPUT_FILE"
    exit 1
fi

if ! docker ps | grep -q ir_mongodb; then
    echo "MongoDB не запущен. Запускаю..."
    docker compose up -d mongodb
    sleep 5
fi

if [[ "$INPUT_FILE" == *.gz ]]; then
    echo "Распаковка архива..."
    gunzip -k "$INPUT_FILE"
    INPUT_FILE="${INPUT_FILE%.gz}"
    TEMP_FILE=true
fi

echo "Импорт корпуса..."
docker cp "$INPUT_FILE" ir_mongodb:/data/db/import.json

docker exec ir_mongodb mongoimport \
    --db=medical_search \
    --collection=articles \
    --file=/data/db/import.json \
    --drop

docker exec ir_mongodb rm /data/db/import.json

if [ "$TEMP_FILE" = true ]; then
    rm "$INPUT_FILE"
fi

echo ""
echo "Готово!"
docker exec ir_mongodb mongosh medical_search --quiet --eval "print('Импортировано документов: ' + db.articles.countDocuments({}))"

