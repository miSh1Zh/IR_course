#!/bin/bash
set -e

cd "$(dirname "$0")/.."

if ! docker ps | grep -q ir_mongodb; then
    echo "Ошибка: MongoDB не запущен"
    exit 1
fi

OUTPUT_FILE="corpus_$(date +%Y%m%d).json"

echo "Экспорт корпуса..."
docker exec ir_mongodb mongoexport \
    --db=medical_search \
    --collection=articles \
    --out=/data/db/export.json

docker cp ir_mongodb:/data/db/export.json "./$OUTPUT_FILE"
docker exec ir_mongodb rm /data/db/export.json

COUNT=$(wc -l < "$OUTPUT_FILE")
SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)

echo "Архивирование..."
gzip "$OUTPUT_FILE"

echo ""
echo "Готово!"
echo "Файл: ${OUTPUT_FILE}.gz"
echo "Документов: $COUNT"
echo "Размер: $(du -h "${OUTPUT_FILE}.gz" | cut -f1)"
echo ""
echo "Для импорта:"
echo "  ./scripts/import_corpus.sh ${OUTPUT_FILE}.gz"

