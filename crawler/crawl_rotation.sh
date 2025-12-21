#!/bin/bash
set -e

# Конфигурация
JOURNALDOCTOR_TIME=5  # минут для journaldoctor
BNEWS_TIME=5           # минут для bnews
RMJ_TIME=5            # минут для rmj
PAUSE_BETWEEN=2        # минут пауза между сменой источника
LONG_PAUSE=30          # минут пауза при блокировке всех источников
MIN_ITEMS=5            # минимум документов за сессию для считания источника активным

echo "Стратегия: по очереди с ограничением времени"
echo "journaldoctor: ${JOURNALDOCTOR_TIME} мин"
echo "bnews: ${BNEWS_TIME} мин"
echo "rmj: ${RMJ_TIME} мин"
echo ""

# Счётчик циклов
CYCLE=1

# Функция для подсчета собранных документов
count_items() {
    local spider_name=$1
    local log_file="/app/logs/${spider_name}_stats.log"
    
    # Ищем строку вида "item_scraped_count': 123" в логах Scrapy
    scrapy crawl "$spider_name" -L INFO 2>&1 | tee "$log_file" &
    local pid=$!
    
    # Ждем завершения с таймаутом
    local time_limit=$2
    timeout "${time_limit}m" wait $pid 2>/dev/null || true
    
    # Извлекаем количество собранных items
    local count=$(grep -oP "item_scraped_count': \K\d+" "$log_file" 2>/dev/null | tail -1)
    echo "${count:-0}"
}

while true; do
    echo "Цикл ${CYCLE}"
    
    blocked_count=0
    
    # 1. journaldoctor
    echo ""
    echo "[$(date +%H:%M:%S)] === journaldoctor (${JOURNALDOCTOR_TIME} мин) ==="
    items_before=$(docker exec ir_mongodb mongosh medical_search --quiet --eval "db.articles.countDocuments({source: 'journaldoctor'})" 2>/dev/null || echo "0")
    timeout ${JOURNALDOCTOR_TIME}m scrapy crawl journaldoctor -L INFO || true
    items_after=$(docker exec ir_mongodb mongosh medical_search --quiet --eval "db.articles.countDocuments({source: 'journaldoctor'})" 2>/dev/null || echo "0")
    items_collected=$((items_after - items_before))
    
    echo "[$(date +%H:%M:%S)] Собрано документов: ${items_collected}"
    if [ "$items_collected" -lt "$MIN_ITEMS" ]; then
        echo "[$(date +%H:%M:%S)] ВНИМАНИЕ: journaldoctor может быть заблокирован (собрано < ${MIN_ITEMS})"
        blocked_count=$((blocked_count + 1))
    fi
    
    echo "[$(date +%H:%M:%S)] Пауза ${PAUSE_BETWEEN} мин..."
    sleep ${PAUSE_BETWEEN}m
    
    # 2. bnews
    echo ""
    echo "[$(date +%H:%M:%S)] === bnews (${BNEWS_TIME} мин) ==="
    items_before=$(docker exec ir_mongodb mongosh medical_search --quiet --eval "db.articles.countDocuments({source: 'bnews'})" 2>/dev/null || echo "0")
    timeout ${BNEWS_TIME}m scrapy crawl bnews -L INFO || true
    items_after=$(docker exec ir_mongodb mongosh medical_search --quiet --eval "db.articles.countDocuments({source: 'bnews'})" 2>/dev/null || echo "0")
    items_collected=$((items_after - items_before))
    
    echo "[$(date +%H:%M:%S)] Собрано документов: ${items_collected}"
    if [ "$items_collected" -lt "$MIN_ITEMS" ]; then
        echo "[$(date +%H:%M:%S)] ВНИМАНИЕ: bnews может быть заблокирован (собрано < ${MIN_ITEMS})"
        blocked_count=$((blocked_count + 1))
    fi
    
    echo "[$(date +%H:%M:%S)] Пауза ${PAUSE_BETWEEN} мин..."
    sleep ${PAUSE_BETWEEN}m
    
    # 3. rmj
    echo ""
    echo "[$(date +%H:%M:%S)] === rmj (${RMJ_TIME} мин) ==="
    items_before=$(docker exec ir_mongodb mongosh medical_search --quiet --eval "db.articles.countDocuments({source: 'rmj'})" 2>/dev/null || echo "0")
    timeout ${RMJ_TIME}m scrapy crawl rmj -L INFO || true
    items_after=$(docker exec ir_mongodb mongosh medical_search --quiet --eval "db.articles.countDocuments({source: 'rmj'})" 2>/dev/null || echo "0")
    items_collected=$((items_after - items_before))
    
    echo "[$(date +%H:%M:%S)] Собрано документов: ${items_collected}"
    if [ "$items_collected" -lt "$MIN_ITEMS" ]; then
        echo "[$(date +%H:%M:%S)] ВНИМАНИЕ: rmj может быть заблокирован (собрано < ${MIN_ITEMS})"
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
    
    CYCLE=$((CYCLE + 1))
    
    echo ""
    echo "[$(date +%H:%M:%S)] Цикл завершён. Начинаем следующий..."
    echo ""
done

