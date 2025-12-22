import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
from urllib.parse import unquote
import re


class WikipediaSpider(scrapy.Spider):
    """Spider для сбора статей с ru.wikipedia.org"""
    
    name = 'wikipedia'
    allowed_domains = ['ru.wikipedia.org']
    
    start_urls = [
        'https://ru.wikipedia.org/wiki/Медицина',
        'https://ru.wikipedia.org/wiki/Категория:Медицина',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания',
        'https://ru.wikipedia.org/wiki/Категория:Анатомия',
        'https://ru.wikipedia.org/wiki/Категория:Биология',
    ]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 10,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'MedicalSearchBot/1.0 (Educational project; +https://github.com/example)',
        'JOBDIR': 'logs/wikipedia_state',
    }
    
    def parse(self, response):
        """Парсинг страницы Wikipedia"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Декодируем URL для проверки (кириллица в URL кодируется)
        decoded_url = unquote(response.url)
        
        # Пропускаем служебные страницы
        skip_patterns = ['Служебная:', 'Обсуждение:', 'Участник:', 'Файл:', 'Шаблон:', 'Портал:', 'Справка:']
        if any(x in decoded_url for x in skip_patterns):
            return
        
        # Если это страница категории — собираем ссылки
        if 'Категория:' in decoded_url or '/wiki/Category:' in response.url:
            self.logger.info(f"Обработка категории: {decoded_url}")
            
            # Статьи в категории
            for link in response.css('#mw-pages a::attr(href)').getall():
                if link and link.startswith('/wiki/') and ':' not in link:
                    self.logger.debug(f"Найдена статья: {link}")
                    yield response.follow(link, self.parse)
            
            # Подкатегории
            for link in response.css('#mw-subcategories a::attr(href)').getall():
                if link and '/wiki/' in link:
                    decoded_link = unquote(link)
                    if 'Категория:' in decoded_link or 'Category:' in link:
                        self.logger.debug(f"Найдена подкатегория: {link}")
                        yield response.follow(link, self.parse)
            
            # Пагинация категории (следующая страница)
            next_page = response.css('a:contains("следующая страница")::attr(href), a:contains("Следующая страница")::attr(href)').get()
            if next_page:
                self.logger.info(f"Пагинация: {next_page}")
                yield response.follow(next_page, self.parse)
        else:
            # Это статья — извлекаем данные
            yield from self.parse_article(response)
    
    def parse_article(self, response):
        """Парсинг статьи Wikipedia"""
        # Заголовок
        title = response.css('#firstHeading::text').get()
        if not title:
            title = response.css('h1::text').get()
        
        if not title:
            return
        
        title = title.strip()
        
        # Текст статьи
        text_parts = response.css(
            '#mw-content-text .mw-parser-output > p::text, '
            '#mw-content-text .mw-parser-output > p b::text, '
            '#mw-content-text .mw-parser-output > p i::text, '
            '#mw-content-text .mw-parser-output > p a::text'
        ).getall()
        
        text = ' '.join([p.strip() for p in text_parts if p.strip()])
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\[\d+\]', '', text)  # Убираем [1], [2]
        
        if len(text) < 200:
            return
        
        # Категория (первая из списка)
        categories = response.css('#mw-normal-catlinks a::text').getall()
        category = categories[0] if categories else None
        
        item = MedicalArticle()
        item['source'] = 'wikipedia'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = None
        item['crawled_at'] = datetime.now().isoformat()
        
        self.logger.info(f"Собрана статья: {title[:50]}...")
        yield item

