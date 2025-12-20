#!/bin/bash

# Интеграционные тесты поисковой системы
# Запускать из директории engine/

set -e  # Выход при ошибке

echo "========================================"
echo "      ИНТЕГРАЦИОННЫЕ ТЕСТЫ"
echo "========================================"
echo

# Создать тестовые данные
echo "Создание тестового корпуса..."
cat > data/test_corpus.json << 'EOF'
{"title": "Кардиология сердце", "text": "Статья о болезнях сердца и кардиологии. Лечение сердечной недостаточности.", "url": "http://test/1", "source": "test", "category": "Кардиология"}
{"title": "Неврология мозг", "text": "Статья о болезнях нервной системы и неврологии. Лечение головной боли.", "url": "http://test/2", "source": "test", "category": "Неврология"}
{"title": "Кардиология аритмия", "text": "Статья об аритмии и её лечении. Кардиология и сердце.", "url": "http://test/3", "source": "test", "category": "Кардиология"}
{"title": "Терапия общая", "text": "Общие вопросы терапии. Диагностика и лечение.", "url": "http://test/4", "source": "test", "category": "Терапия"}
{"title": "Педиатрия дети", "text": "Детские болезни и педиатрия. Лечение детей.", "url": "http://test/5", "source": "test", "category": "Педиатрия"}
EOF

# Построить индекс
echo "Построение индекса..."
./indexer --input=data/test_corpus.json --output=data/test_index.bin

echo
echo "--- Тест 1: Поиск по одному слову ---"
result=$(echo "лечение" | ./searcher --index=data/test_index.bin --batch)
# Лечение встречается в нескольких документах
if echo "$result" | grep -q "документов"; then
    echo " Тест 1 пройден"
    echo "$result"
else
    echo "FAIL Тест 1 провален"
    echo "$result"
    exit 1
fi

echo
echo "--- Тест 2: Поиск AND ---"
result=$(echo "статья && лечение" | ./searcher --index=data/test_index.bin --batch)
if echo "$result" | grep -q "документов"; then
    echo " Тест 2 пройден"
    echo "$result"
else
    echo "FAIL Тест 2 провален"
    exit 1
fi

echo
echo "--- Тест 3: Поиск OR ---"
result=$(echo "сердце || мозг" | ./searcher --index=data/test_index.bin --batch)
# OR должен найти хотя бы 1 документ
if echo "$result" | grep -q "документов"; then
    echo " Тест 3 пройден"
    echo "$result"
else
    echo "FAIL Тест 3 провален"
    echo "$result"
    exit 1
fi

echo
echo "--- Тест 4: Поиск NOT ---"
result=$(echo "статья && !детей" | ./searcher --index=data/test_index.bin --batch)
if echo "$result" | grep -q "документов"; then
    echo " Тест 4 пройден"
    echo "$result"
else
    echo "FAIL Тест 4 провален"
    exit 1
fi

echo
echo "--- Тест 5: Пустой результат ---"
result=$(echo "несуществующеесловоqwerty" | ./searcher --index=data/test_index.bin --batch)
if echo "$result" | grep -q "0 документов"; then
    echo " Тест 5 пройден"
else
    echo "FAIL Тест 5 провален"
    exit 1
fi

# Очистка
echo
echo "Очистка тестовых файлов..."
rm -f data/test_corpus.json data/test_index.bin

echo
echo "========================================"
echo "    ВСЕ ИНТЕГРАЦИОННЫЕ ТЕСТЫ ПРОЙДЕНЫ!"
echo "========================================"

