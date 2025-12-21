#!/bin/bash
set -e

# Конфигурация
JOURNALDOCTOR_TIME=15  # минут для journaldoctor
BNEWS_TIME=10          # минут для bnews
RMJ_TIME=20            # минут для rmj (самый большой)
PAUSE_BETWEEN=5        # минут пауза между сменой источника (увеличена)
LONG_PAUSE=60          # минут пауза при блокировке всех источников
MIN_ITEMS=3            # минимум документов за сессию (уменьшен с 5 до 3)

# MongoDB connection (внутри Docker сети)
MONGO_HOST="${MONGO_HOST:-mongodb}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DB="${MONGO_DB:-medical_search}"

echo "Стратегия:"
echo "journaldoctor: ${JOURNALDOCTOR_TIME} мин"
echo "bnews: ${BNEWS_TIME} мин"
echo "rmj: ${RMJ_TIME} мин"
echo "MongoDB: ${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}"
echo ""

# Функция для подсчета документов в MongoDB
count_docs() {
    local source=$1
    # Используем Python с pymongo для подсчета
    python3 -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://${MONGO_HOST}:${MONGO_PORT}/')
    db = client['${MONGO_DB}']
    count = db.articles.count_documents({'source': '${source}'})
    print(count)
except:
    print(0)
" 2>/dev/null || echo "0"
}

# Счётчик циклов
CYCLE=1

while true; do
    echo "Цикл ${CYCLE}"
    
    blocked_count=0
    
    # 1. journaldoctor
    echo ""
    echo "[$(date +%H:%M:%S)] === journaldoctor (${JOURNALDOCTOR_TIME} мин) ==="
    items_before=$(count_docs "journaldoctor")
    echo "[$(date +%H:%M:%S)] Документов до: ${items_before}"
    
    timeout ${JOURNALDOCTOR_TIME}m scrapy crawl journaldoctor -L INFO 2>&1 | tee -a /app/logs/rotation.log || true
    
    items_after=$(count_docs "journaldoctor")
    items_collected=$((items_after - items_before))
    
    echo "[$(date +%H:%M:%S)] Документов после: ${items_after}"
    echo "[$(date +%H:%M:%S)] Собрано: ${items_collected}"
    if [ "$items_collected" -lt "$MIN_ITEMS" ]; then
        echo "[$(date +%H:%M:%S)] journaldoctor может быть заблокирован (< ${MIN_ITEMS})"
        blocked_count=$((blocked_count + 1))
    fi
    
    echo "[$(date +%H:%M:%S)] Пауза ${PAUSE_BETWEEN} мин..."
    sleep ${PAUSE_BETWEEN}m
    
    # 2. bnews
    echo ""
    echo "[$(date +%H:%M:%S)] === bnews (${BNEWS_TIME} мин) ==="
    items_before=$(count_docs "bnews")
    echo "[$(date +%H:%M:%S)] Документов до: ${items_before}"
    
    timeout ${BNEWS_TIME}m scrapy crawl bnews -L INFO 2>&1 | tee -a /app/logs/rotation.log || true
    
    items_after=$(count_docs "bnews")
    items_collected=$((items_after - items_before))
    
    echo "[$(date +%H:%M:%S)] Документов после: ${items_after}"
    echo "[$(date +%H:%M:%S)] Собрано: ${items_collected}"
    if [ "$items_collected" -lt "$MIN_ITEMS" ]; then
        echo "[$(date +%H:%M:%S)] bnews может быть заблокирован (< ${MIN_ITEMS})"
        blocked_count=$((blocked_count + 1))
    fi
    
    echo "[$(date +%H:%M:%S)] Пауза ${PAUSE_BETWEEN} мин..."
    sleep ${PAUSE_BETWEEN}m
    
    # 3. rmj
    echo ""
    echo "[$(date +%H:%M:%S)] === rmj (${RMJ_TIME} мин) ==="
    items_before=$(count_docs "rmj")
    echo "[$(date +%H:%M:%S)] Документов до: ${items_before}"
    
    timeout ${RMJ_TIME}m scrapy crawl rmj -L INFO 2>&1 | tee -a /app/logs/rotation.log || true
    
    items_after=$(count_docs "rmj")
    items_collected=$((items_after - items_before))
    
    echo "[$(date +%H:%M:%S)] Документов после: ${items_after}"
    echo "[$(date +%H:%M:%S)] Собрано: ${items_collected}"
    if [ "$items_collected" -lt "$MIN_ITEMS" ]; then
        echo "[$(date +%H:%M:%S)] rmj может быть заблокирован (< ${MIN_ITEMS})"
        blocked_count=$((blocked_count + 1))
    fi
    
    # Проверка: если все источники заблокированы
    if [ "$blocked_count" -eq 3 ]; then
        echo ""
        echo "[$(date +%H:%M:%S)] ВСЕ ИСТОЧНИКИ ЗАБЛОКИРОВАНЫ ИЛИ НЕДОСТУПНЫ"
        echo "[$(date +%H:%M:%S)] Увеличенная пауза: ${LONG_PAUSE} мин..."
        sleep ${LONG_PAUSE}m
    else
        echo "[$(date +%H:%M:%S)] Пауза ${PAUSE_BETWEEN} мин..."
        sleep ${PAUSE_BETWEEN}m
    fi
    
    
    echo ""
    echo "[$(date +%H:%M:%S)] Цикл ${CYCLE} завершён. Начинаем следующий..."
    echo ""
    
    CYCLE=$((CYCLE + 1))
done

