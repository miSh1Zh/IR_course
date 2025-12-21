#!/bin/bash
set -e

echo "Запуск всех spider'ов..."

echo "=== journaldoctor ==="
scrapy crawl journaldoctor -L INFO

echo "=== bnews ==="
scrapy crawl bnews -L INFO

echo "=== rmj ==="
scrapy crawl rmj -L INFO

echo "Краулинг завершен."

