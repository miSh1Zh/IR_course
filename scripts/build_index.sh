#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Экспорт корпуса из MongoDB..."
if ! docker ps | grep -q ir_mongodb; then
    echo "Ошибка: MongoDB не запущен"
    exit 1
fi

NETWORK=$(docker inspect ir_mongodb --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')

docker run --rm \
    --network "$NETWORK" \
    -v "$(pwd):/workspace" \
    -e MONGO_URI=mongodb://ir_mongodb:27017/ \
    python:3.11-slim \
    bash -c "pip install -q pymongo && cd /workspace/scripts && python export_corpus.py"

echo ""
echo "Построение индекса..."
cd engine
make clean
make all

echo ""
echo "Индексация корпуса..."
./indexer --input=../data/corpus.json --output=../data/index.bin

echo ""
echo "Готово! Индекс сохранен: data/index.bin"

