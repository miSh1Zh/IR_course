import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class JournalDoctorSpider(scrapy.Spider):
    """Spider для сбора статей с journaldoctor.ru
    
    Рекурсивный обход всех страниц сайта с глубиной 7.
    """
    
    name = 'journaldoctor'
    allowed_domains = ['journaldoctor.ru']
    
    start_urls = ['https://journaldoctor.ru/']
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 7,
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'JOBDIR': '/app/logs/journaldoctor_state',
    }
    
    def parse(self, response):
        """Рекурсивный обход всех страниц"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Пробуем извлечь статью с текущей страницы
        yield from self.try_parse_article(response)
        
        # Рекурсивно следуем по всем внутренним ссылкам
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            # Пропускаем внешние ссылки и файлы
            if 'journaldoctor.ru' not in full_url:
                continue
            if any(ext in full_url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js']):
                continue
            
            yield response.follow(full_url, self.parse)
    
    def try_parse_article(self, response):
        """Попытка извлечь статью со страницы"""
        
        # Заголовок
        title = response.css('h1::text').get()
        if not title:
            title = response.css('.article-title::text, title::text').get()
        
        if not title:
            return
        
        title = title.strip()
        
        # Пропускаем служебные страницы
        skip_titles = ['каталог', 'главная', 'контакты', 'о нас', 'поиск', 'catalog']
        if any(skip in title.lower() for skip in skip_titles):
            return
        
        # Текст статьи
        text_parts = []
        
        for selector in [
            '#tabs-1 p::text',
            '#tabs-2 p::text',
            '#tabs-3 p::text',
            '.tab-content p::text',
            '.article-content p::text',
            'article p::text',
            '.content p::text',
        ]:
            parts = response.css(selector).getall()
            if parts:
                text_parts.extend(parts)
        
        if not text_parts:
            text_parts = response.css('p::text').getall()
        
        text = ' '.join(text_parts).strip()
        text = re.sub(r'\s+', ' ', text)
        
        if len(text) < 100:
            return
        
        # Категория
        category = response.css('.category::text, .tag::text, .rubric::text').get()
        if category:
            category = category.strip()
        
        # Год
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
        
        item = MedicalArticle()
        item['source'] = 'journaldoctor'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        yield item
