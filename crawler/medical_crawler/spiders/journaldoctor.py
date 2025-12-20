import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class JournalDoctorSpider(scrapy.Spider):
    """Spider для сбора статей с journaldoctor.ru"""
    
    name = 'journaldoctor'
    allowed_domains = ['journaldoctor.ru']
    
    # Начать с каталога статей
    start_urls = ['https://journaldoctor.ru/catalog']
    
    # Ограничения для теста
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 6,                # Не уходить глубже 6 уровней
        'ROBOTSTXT_OBEY': False,         # Для учебных целей (robots.txt блокирует архивы)
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }
    
    def parse(self, response):
        """Парсинг страниц каталога статей"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Найти все ссылки на статьи в каталоге
        # На странице /catalog/ статьи имеют ссылки вида /catalog/XXX/statya-название/
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
                
            full_url = response.urljoin(link)
            
            # Статьи: /catalog/название-раздела/название-статьи/
            # Или PDF-ссылки (пропускаем)
            if '.pdf' in full_url.lower():
                continue
                
            # Ссылки на разделы или статьи в /catalog/
            if '/catalog/' in full_url:
                # Если это не главная страница каталога и не фильтр
                if full_url.rstrip('/') != 'https://journaldoctor.ru/catalog' and '?' not in full_url:
                    yield response.follow(full_url, self.parse_article)
        
        # Следовать по пагинации
        for next_page in response.xpath('//a[contains(@class, "page")]/@href | //a[contains(text(), "→")]/@href').getall():
            if next_page:
                yield response.follow(next_page, self.parse)
        
        # Обход архива по годам (2007-2025)
        for year in range(2007, 2026):
            year_url = f"https://journaldoctor.ru/catalog/{year}/"
            yield scrapy.Request(year_url, callback=self.parse, dont_filter=False)
    
    def parse_article(self, response):
        """Парсинг отдельной статьи"""
        
        # Извлечь заголовок
        title = response.css('h1::text').get()
        if not title:
            title = response.css('.article-title::text, title::text').get()
        
        if not title:
            self.logger.debug(f"Нет заголовка: {response.url}")
            return
        
        title = title.strip()
        
        # Извлечь текст статьи
        text_parts = []
        
        # На journaldoctor.ru текст статьи находится в табах: Резюме, Основные положения и т.д.
        # Собираем весь текст из различных блоков
        for selector in [
            '#tabs-1 p',           # Резюме
            '#tabs-2 p',           # Основные положения  
            '#tabs-3 p',           # Заключение
            '.tab-content p',      # Общий селектор для табов
            'article p',           # Альтернатива
            '.article-content p',
        ]:
            parts = response.css(f'{selector}::text').getall()
            if parts:
                text_parts.extend(parts)
        
        # Если не нашли в табах, ищем весь текст
        if not text_parts:
            text_parts = response.css('p::text').getall()
        
        text = ' '.join(text_parts).strip()
        text = re.sub(r'\s+', ' ', text)
        
        if len(text) < 100:
            self.logger.debug(f"Слишком короткий текст ({len(text)} символов): {response.url}")
            return
        
        # Извлечь категорию
        category = response.css('.category::text, .tag::text, .rubric::text').get()
        if category:
            category = category.strip()
        
        # Извлечь год
        year = None
        year_match = re.search(r'20\d{2}', response.url)
        if year_match:
            year = year_match.group()
        else:
            date_text = response.css('.date::text, .published::text, time::text').get()
            if date_text:
                year_match = re.search(r'20\d{2}', date_text)
                if year_match:
                    year = year_match.group()
        
        # Создать item
        item = MedicalArticle()
        item['source'] = 'journaldoctor'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        yield item

