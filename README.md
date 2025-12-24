# Система информационного поиска по медицинским статьям

Поисковая система с веб-краулером, инвертированным индексом и булевым поиском.

## Быстрый старт

После клонирования репозитория:

```bash
# 1. Запустить MongoDB
make start

# 2. Импортировать готовый корпус (если есть)
make import FILE=corpus.json.gz

# Или собрать корпус самостоятельно
make crawl

# 3. Построить индекс
make build-index

# 4. Запустить веб-интерфейс
make web
```

Веб-интерфейс: http://localhost:5001

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
```

### Импорт/экспорт

```bash
make export                        # Экспорт корпуса
make import FILE=corpus.json.gz    # Импорт корпуса
```

Корпус из 30137 документов можно найти по [ссылке](https://drive.google.com/file/d/18wUGC9AU5tMld5kNqrdn6AxKwHTttNBu/view?usp=drive_link)


## Поиск через CLI

```bash
cd engine
./searcher --index=../data/index.bin --query="кардиология"
./searcher --index=../data/index.bin --query="диабет && лечение"
./searcher --index=../data/index.bin --query="сердце || мозг"
```

## Компоненты

**Crawler** — Scrapy spider для сбора статей из медицинских журналов:
- journaldoctor.ru — медицинский журнал
- b-news.media — новости биотехнологий BIOCAD
- rmj.ru — русский медицинский журнал
- takzdorovo.ru — портал о ЗОЖ Минздрава РФ
- probolezny.ru — энциклопедия заболеваний
- клиникакраснодар.рф — медицинская клиника
- bigenc.ru — Большая российская энциклопедия (медицина, биология, психология)
- wikipedia - энциклопедия (категории, связанные с медицинской тематикой)
- ruwiki - тоже энциклопедия, тоже с фильтрацией по категориям, связанным с медицинской тематикой

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
make zipf                    # Анализ закона Ципфа
```

Готовую статистику по собранному корпусу можно найти по [ссылке](https://drive.google.com/drive/folders/1ldakc9nADI2tKb16UnSspYPMyxfGcEvA?usp=drive_link)
