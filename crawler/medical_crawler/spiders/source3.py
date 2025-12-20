import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class Source3Spider(scrapy.Spider):
    """Spider для третьего источника медицинских статей
    
    TODO: Заменить на реальный источник медицинских статей
    Примеры возможных источников:
    - rmj.ru (Русский медицинский журнал)
    - pediatr-russia.ru
    - cardiojournal.ru
    """
    
    name = 'source3'
    allowed_domains = ['example-medical-source3.ru']  # TODO: заменить
    
    start_urls = ['https://example-medical-source3.ru/']  # TODO: заменить
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 15000,
        'DEPTH_LIMIT': 5,
    }
    
    def parse(self, response):
        """Парсинг каталога статей"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # TODO: Адаптировать селекторы под реальный источник
        for link in response.css('a.article-link::attr(href)').getall():
            if link:
                yield response.follow(link, self.parse_article)
        
        # Пагинация
        for next_page in response.css('a.next::attr(href)').getall():
            if next_page:
                yield response.follow(next_page, self.parse)
    
    def parse_article(self, response):
        """Парсинг статьи"""
        
        title = response.css('h1::text').get()
        if not title:
            return
        
        title = title.strip()
        
        # TODO: Адаптировать селекторы под реальный источник
        text_parts = response.css('.article-content p::text').getall()
        text = ' '.join(text_parts).strip()
        text = re.sub(r'\s+', ' ', text)
        
        if len(text) < 100:
            return
        
        category = response.css('.category::text').get()
        year = None
        year_match = re.search(r'20\d{2}', response.url)
        if year_match:
            year = year_match.group()
        
        item = MedicalArticle()
        item['source'] = 'source3'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category.strip() if category else None
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        yield item

