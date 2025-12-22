#!/bin/bash
set -e

echo "Запуск всех spider'ов..."

echo "=== journaldoctor ==="
scrapy crawl journaldoctor -L INFO

echo "=== bnews ==="
scrapy crawl bnews -L INFO

echo "=== rmj ==="
scrapy crawl rmj -L INFO

echo "=== takzdorovo ==="
scrapy crawl takzdorovo -L INFO

echo "=== probolezny ==="
scrapy crawl probolezny -L INFO

echo "=== clinickrasnodar ==="
scrapy crawl clinickrasnodar -L INFO

echo "=== bigenc ==="
scrapy crawl bigenc -L INFO

echo "=== wikipedia ==="
scrapy crawl wikipedia -L INFO

echo "Краулинг завершен."

