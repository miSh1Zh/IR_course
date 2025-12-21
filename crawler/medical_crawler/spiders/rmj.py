import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class RMJSpider(scrapy.Spider):
    """Spider для сбора статей с rmj.ru (Русский медицинский журнал)
    
    Структура URL:
    /articles/{категория}/{название_статьи}/
    
    Пример: /articles/endokrinologiya/Klinicheskoe_nablyudenie_.../
    """
    
    name = 'rmj'
    allowed_domains = ['rmj.ru', 'www.rmj.ru']
    
    # Список основных категорий rmj.ru
    categories = [
        'nevrologiya', 'kardiologiya', 'endokrinologiya', 'gastroenterologiya',
        'pulmonologiya', 'revmatologiya', 'dermatologiya', 'oftalmologiya',
        'otorinolaringologiya', 'urologiya', 'ginekologiya', 'akusherstvo',
        'pediatriya', 'onkologiya', 'allergologiya', 'immunologiya',
        'infektsionnye_bolezni', 'khirurgiya', 'travmatologiya', 'ortopediya',
        'psihiatriya', 'terapiya', 'obschaya_vrachebnaya_praktika',
        'anesteziologiya', 'reanimatologiya', 'nefrologyia', 'gematologiya',
    ]
    
    start_urls = ['https://www.rmj.ru/articles/']
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 4,
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'COOKIES_ENABLED': True,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        },
    }
    
    def start_requests(self):
        """Генерация запросов для каждой категории"""
        # Сначала главная страница каталога
        yield scrapy.Request(
            'https://www.rmj.ru/articles/',
            callback=self.parse_catalog
        )
        
        # Затем каждая категория
        for cat in self.categories:
            url = f'https://www.rmj.ru/articles/{cat}/'
            yield scrapy.Request(url, callback=self.parse_category, meta={'category': cat})
    
    def parse_catalog(self, response):
        """Парсинг главной страницы каталога - поиск ссылок на категории и статьи"""
        self.logger.info(f"Парсинг каталога: {response.url}")
        
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            if '/articles/' in full_url and full_url != 'https://www.rmj.ru/articles/':
                # Определить тип ссылки
                path = full_url.replace('https://www.rmj.ru/articles/', '').strip('/')
                parts = path.split('/')
                
                if len(parts) == 1 and parts[0]:
                    # Категория
                    yield response.follow(full_url, self.parse_category, meta={'category': parts[0]})
                elif len(parts) >= 2:
                    # Статья
                    yield response.follow(full_url, self.parse_article, meta={'category': parts[0]})
    
    def parse_category(self, response):
        """Парсинг страницы категории"""
        category = response.meta.get('category', '')
        self.logger.info(f"Парсинг категории '{category}': {response.url}")
        
        # Ссылки на статьи
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            # Статьи этой категории
            if f'/articles/{category}/' in full_url:
                path = full_url.replace(f'https://www.rmj.ru/articles/{category}/', '').strip('/')
                if path and '/' not in path and not path.startswith('?'):
                    yield response.follow(full_url, self.parse_article, meta={'category': category})
        
        # Пагинация
        for page_link in response.css('a.pagination__link::attr(href), .pagination a::attr(href)').getall():
            if page_link:
                yield response.follow(page_link, self.parse_category, meta={'category': category})
    
    def parse_article(self, response):
        """Парсинг статьи"""
        
        # Заголовок
        title = response.css('h1::text').get()
        if not title:
            title = response.css('meta[property="og:title"]::attr(content)').get()
        if not title:
            title = response.css('.article-title::text').get()
        
        if not title:
            return
        
        title = title.strip()
        
        # Текст статьи - резюме и основной текст
        text_parts = []
        
        # Резюме статьи
        for selector in [
            '.article-resume p::text',
            '.article-abstract p::text',
            '.resume p::text',
            '#resume p::text',
            '.article-text p::text',
            '.article-content p::text',
            'article p::text',
        ]:
            parts = response.css(selector).getall()
            if parts:
                text_parts.extend(parts)
        
        # Если не нашли, попробовать meta description
        if not text_parts:
            desc = response.css('meta[name="description"]::attr(content)').get()
            if desc:
                text_parts.append(desc)
        
        # Общий текст страницы
        if not text_parts:
            text_parts = response.css('p::text').getall()
        
        text = ' '.join(text_parts).strip()
        text = re.sub(r'\s+', ' ', text)
        
        if len(text) < 100:
            return
        
        # Категория
        category = response.meta.get('category')
        if not category:
            url_match = re.search(r'/articles/([^/]+)/', response.url)
            if url_match:
                category = url_match.group(1)
        
        # Год публикации
        year = None
        date_text = response.css('.article-date::text, .date::text, time::text').get()
        if date_text:
            year_match = re.search(r'20\d{2}', date_text)
            if year_match:
                year = year_match.group()
        
        if not year:
            # Попробовать из meta
            date_meta = response.css('meta[property="article:published_time"]::attr(content)').get()
            if date_meta:
                year_match = re.search(r'20\d{2}', date_meta)
                if year_match:
                    year = year_match.group()
        
        item = MedicalArticle()
        item['source'] = 'rmj'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        yield item

