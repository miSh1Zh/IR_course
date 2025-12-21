.PHONY: help start stop restart crawl export import build-index stats zipf test clean

help:
	@echo "Makefile для управления IR проектом"
	@echo ""
	@echo "Основные команды:"
	@echo "  make start        - Запустить MongoDB"
	@echo "  make crawl        - Запустить краулер для сбора корпуса"
	@echo "  make build-index  - Экспорт корпуса и построение индекса"
	@echo "  make stats        - Показать статистику корпуса"
	@echo "  make zipf         - Проверить закон Ципфа"
	@echo "  make test         - Запустить unit-тесты"
	@echo "  make web          - Запустить веб-интерфейс"
	@echo "  make stop         - Остановить все сервисы"
	@echo "  make clean        - Удалить временные файлы"
	@echo ""
	@echo "Импорт/экспорт:"
	@echo "  make export       - Экспортировать корпус для передачи"
	@echo "  make import FILE=<файл> - Импортировать корпус"

start:
	@echo "Запуск MongoDB..."
	docker compose up -d mongodb
	@sleep 3
	@echo "MongoDB запущен"

stop:
	@echo "Остановка сервисов..."
	docker compose down

restart: stop start

crawl: start
	@echo "Запуск краулера..."
	docker compose up -d crawler

export:
	@echo "Экспорт корпуса..."
	./scripts/export_for_share.sh

import:
ifndef FILE
	@echo "Ошибка: укажите файл для импорта"
	@echo "Использование: make import FILE=corpus.json.gz"
	@exit 1
endif
	@echo "Импорт корпуса из $(FILE)..."
	./scripts/import_corpus.sh $(FILE)

build-index: start
	@echo "Экспорт и построение индекса..."
	./scripts/build_index.sh

stats: start
	@echo "Статистика корпуса..."
	@docker ps | grep -q ir_mongodb || (echo "MongoDB не запущен" && exit 1)
	@NETWORK=$$(docker inspect ir_mongodb --format='{{range $$k,$$v := .NetworkSettings.Networks}}{{$$k}}{{end}}') && \
	docker run --rm \
		--network "$$NETWORK" \
		-v "$$(pwd)/analysis:/app" \
		-e MONGO_URI=mongodb://ir_mongodb:27017/ \
		python:3.11-slim \
		bash -c "pip install -q pymongo && cd /app && python corpus_stats.py"

zipf:
	@if [ ! -f data/index.bin ]; then \
		echo "Ошибка: индекс не найден. Выполните 'make build-index'"; \
		exit 1; \
	fi
	@echo "Анализ закона Ципфа..."
	@docker run --rm \
		-v "$$(pwd):/workspace" \
		-w /workspace/analysis \
		python:3.11-slim \
		bash -c "pip install -q matplotlib numpy && python zipf_law.py ../data/index.bin && echo '' && echo 'График сохранен: analysis/zipf_law.png'"

test:
	@echo "Запуск unit-тестов..."
	cd engine && make test

test-integration:
	@echo "Запуск интеграционных тестов..."
	cd engine/tests && ./integration_test.sh

web: start
	@echo "Запуск веб-интерфейса..."
	docker compose up -d web
	@echo "Веб-интерфейс: http://localhost:5001"

clean:
	@echo "Очистка временных файлов..."
	rm -f analysis/*.png analysis/*.txt
	rm -f analysis/corpus_stats.json
	rm -f corpus_*.json corpus_*.json.gz
	cd engine && make clean

