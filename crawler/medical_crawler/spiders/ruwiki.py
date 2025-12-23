import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
from urllib.parse import unquote
import re


class RuwikiSpider(scrapy.Spider):
    """Spider для сбора статей с ru.ruwiki.ru (альтернатива Википедии)"""

    name = 'ruwiki'
    allowed_domains = ['ru.ruwiki.ru']

    # Главная медицинская категория
    start_urls = [
        'https://ru.ruwiki.ru/wiki/Категория:Медицина',
    ]

    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 10,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'JOBDIR': 'logs/ruwiki_state',
    }

    def parse(self, response):
        """Парсинг категории или списка статей"""
        self.logger.info(f"Парсинг: {response.url}")

        decoded_url = unquote(response.url)

        # Пропускаем служебные страницы
        skip_patterns = ['Служебная:', 'Обсуждение:', 'Участник:', 'Файл:', 'Шаблон:', 'Рувики:']
        if any(x in decoded_url for x in skip_patterns):
            return

        # Если это категория — собираем ссылки
        if 'Категория:' in decoded_url:
            self.logger.info(f"Обработка категории: {decoded_url}")

            # Подкатегории (в div.mw-category)
            for link in response.css('div.mw-category a::attr(href)').getall():
                if link and '/wiki/Категория:' in link:
                    yield response.follow(link, self.parse)

            # Статьи (в div.mw-category, но без "Категория:")
            for link in response.css('div.mw-category a::attr(href)').getall():
                if link and '/wiki/' in link and 'Категория:' not in link:
                    # Дополнительная проверка: не служебная ли
                    if not any(x in link for x in ['Служебная', 'Обсуждение', 'Рувики:Избранные', 'Рувики:Хорошие', 'Рувики:Выверенные']):
                        yield response.follow(link, self.parse_article)

        else:
            # Это статья
            yield from self.parse_article(response)

    def parse_article(self, response):
        """Парсинг статьи"""
        # Заголовок
        title = response.css('h1.firstHeading::text').get()
        if not title:
            title = response.css('h1::text').get()

        if not title:
            return

        title = title.strip()

        # Текст статьи
        text_parts = response.css('div.mw-parser-output p::text').getall()
        text = ' '.join([t.strip() for t in text_parts if t.strip()])
        text = re.sub(r'\s+', ' ', text).strip()

        # Очистка от служебных текстов
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[править[^\]]*\]', '', text)

        if len(text) < 50:
            return

        # Категория (первая из списка)
        categories = response.css('div.mw-normal-catlinks a::text').getall()
        category = categories[0] if categories else 'Медицина'

        item = MedicalArticle()
        item['source'] = 'ruwiki'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = None
        item['crawled_at'] = datetime.now().isoformat()

        self.logger.info(f"Собрана статья: {title[:50]}...")
        yield item

