#!/bin/bash
set -e

cd "$(dirname "$0")"

if ! docker ps | grep -q ir_mongodb; then
    echo "Ошибка: MongoDB контейнер не запущен"
    echo "Запустите: docker compose up -d mongodb"
    exit 1
fi

NETWORK=$(docker inspect ir_mongodb --format='{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{end}}')

if [ -z "$NETWORK" ]; then
    echo "Ошибка: не удалось определить сеть MongoDB"
    exit 1
fi

docker run --rm \
    --network "$NETWORK" \
    -v "$(pwd)/analysis:/app" \
    -e MONGO_URI=mongodb://ir_mongodb:27017/ \
    python:3.11-slim \
    bash -c "
        pip install -q pymongo &&
        cd /app &&
        python corpus_stats.py
    "

echo "Последние добавленные статьи:"
docker exec ir_mongodb mongosh medical_search --quiet --eval "
db.articles.find(
  {text: {\$exists: true, \$ne: ''}},
  {title: 1, url: 1, crawled_at: 1, _id: 0}
).sort({crawled_at: -1}).limit(5).forEach(doc => {
  print('');
  print('Заголовок: ' + doc.title);
  print('URL: ' + doc.url);
  print('Дата: ' + doc.crawled_at);
});
"

