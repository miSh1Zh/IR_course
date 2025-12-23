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
        'DEPTH_LIMIT': 20,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'JOBDIR': 'logs/ruwiki_state',
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    }

    def parse(self, response):
        """Парсинг категории — обход подкатегорий и сбор статей"""
        self.logger.info(f"Категория: {response.url}")

        decoded_url = unquote(response.url)

        # Пропускаем служебные страницы
        skip_patterns = ['Служебная:', 'Обсуждение:', 'Участник:', 'Файл:', 'Шаблон:']
        if any(x in decoded_url for x in skip_patterns):
            return

        # Проверяем, что это категория
        if 'Категория:' not in decoded_url:
            # Это статья, а не категория
            yield from self.parse_article(response)
            return

        # Это категория — обходим все ссылки в div.mw-category
        all_links = response.css('div.mw-category a::attr(href)').getall()

        for link in all_links:
            if not link:
                continue

            full_url = response.urljoin(link)

            # Если это подкатегория — рекурсивный обход
            if '/wiki/Категория:' in full_url:
                # Пропускаем служебные категории
                if any(skip in full_url for skip in ['Рувики:Избранные', 'Рувики:Хорошие', 'Рувики:Выверенные']):
                    continue
                
                self.logger.info(f"Подкатегория: {full_url}")
                yield response.follow(full_url, self.parse)

            # Если это статья (не категория, не служебная) — парсим
            elif '/wiki/' in full_url:
                # Пропускаем служебные категории в самих ссылках
                if not any(x in full_url for x in ['Служебная', 'Обсуждение', 'Рувики:', 'Файл:']):
                    yield response.follow(full_url, self.parse_article)

    def parse_article(self, response):
        """Парсинг статьи"""
        decoded_url = unquote(response.url)

        # Если это опять категория (редирект или ошибка), обработаем как категорию
        if 'Категория:' in decoded_url:
            self.logger.debug(f"Переадресация на категорию: {decoded_url}")
            yield from self.parse(response)
            return

        # Заголовок
        title = response.css('h1.firstHeading::text').get()
        if not title:
            title = response.css('h1::text').get()

        if not title:
            return

        title = title.strip()

        # Текст статьи (все параграфы)
        text_parts = response.css('div.mw-parser-output p::text').getall()
        text = ' '.join([t.strip() for t in text_parts if t.strip()])
        text = re.sub(r'\s+', ' ', text).strip()

        # Очистка от служебных текстов
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[править[^\]]*\]', '', text)

        if len(text) < 30:
            self.logger.debug(f"Текст слишком короткий ({len(text)} символов): {title}")
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
