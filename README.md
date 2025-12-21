# Система информационного поиска по медицинским статьям

Поисковая система с веб-краулером, инвертированным индексом и булевым поиском.

## Структура

```
ir/
├── crawler/         # Scrapy краулер
├── engine/          # C++ поисковый движок
├── web/             # Веб-интерфейс
├── analysis/        # Скрипты анализа
├── scripts/         # Утилиты
├── data/            # Корпус и индекс
├── Makefile         # Команды управления
└── docker-compose.yml
```

Веб-интерфейс: http://localhost:5001

## Команды

### Основные

```bash
make help          # Справка
make start         # Запуск MongoDB
make crawl         # Сбор документов
make build-index   # Построение индекса
make stats         # Статистика корпуса
make zipf          # Анализ закона Ципфа
make test          # Unit-тесты
make web           # Веб-интерфейс
make stop          # Остановка
make all           # Полный цикл
```

### Импорт/экспорт

```bash
make export                        # Экспорт корпуса
make import FILE=corpus.json.gz    # Импорт корпуса
```

## Поиск через CLI

```bash
cd engine
./searcher --index=../data/index.bin --query="кардиология"
./searcher --index=../data/index.bin --query="диабет && лечение"
./searcher --index=../data/index.bin --query="сердце || мозг"
```

## Компоненты

**Crawler** — Scrapy spider для сбора статей из медицинских журналов. Сохраняет в MongoDB.

**Engine** — C++ поисковый движок:
- Токенизатор (UTF-8, кириллица + латиница)
- Стемминг (русский + английский)
- HashMap (своя реализация)
- Инвертированный индекс (бинарный формат)
- Булев поиск (AND, OR, NOT, скобки)

**Web** — Flask интерфейс для поиска и статистики.

**Analysis** — Скрипты для анализа корпуса и проверки закона Ципфа.

## Технологии

- Python 3.11 (Scrapy, Flask)
- C++17 (ограниченный STL: vector, string)
- MongoDB (хранилище корпуса)
- Docker (контейнеризация)

## Тестирование

```bash
make test                    # Unit-тесты
```

## Статистика

```bash
make stats                   # Полная статистика
```

## Результаты

- `data/corpus.json` — экспортированный корпус (NDJSON)
- `data/index.bin` — бинарный индекс
- `analysis/zipf_law.png` — график закона Ципфа
- `analysis/corpus_stats.json` — статистика

