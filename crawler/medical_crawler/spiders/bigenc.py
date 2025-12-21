import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class BigencSpider(scrapy.Spider):
    """Spider для сбора статей с bigenc.ru
    
    Большая российская энциклопедия - медицинские категории:
    - /t/medics — медики
    - /t/biology — биология
    - /t/medicine — медицина
    - /t/psychology — психология
    - /t/internal_organs — внутренние органы
    - /t/symptoms — симптомы
    
    Статьи имеют вид: /c/{slug}
    """
    
    name = 'bigenc'
    allowed_domains = ['bigenc.ru']
    
    start_urls = [
        'https://bigenc.ru/t/medics',
        'https://bigenc.ru/t/biology',
        'https://bigenc.ru/t/medicine',
        'https://bigenc.ru/t/psychology',
        'https://bigenc.ru/t/internal_organs',
        'https://bigenc.ru/t/symptoms',
    ]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 5,
        'DOWNLOAD_DELAY': 4,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'JOBDIR': '/app/logs/bigenc_state',
    }
    
    def parse(self, response):
        """Парсинг страницы категории"""
        self.logger.info(f"Парсинг категории: {response.url}")
        
        # Извлекаем категорию из URL
        category = self._extract_category(response.url)
        
        # Ссылки на статьи имеют вид /c/{slug}
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            # Статья: /c/{slug}
            if '/c/' in full_url:
                # Извлекаем slug
                match = re.search(r'/c/([a-z0-9-]+)', full_url)
                if match:
                    yield response.follow(full_url, self.parse_article, meta={'category': category})
        
        # Пагинация
        next_page = response.css('a.next::attr(href), .pagination a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse, meta={'category': category})
    
    def _extract_category(self, url):
        """Извлечь категорию из URL"""
        categories = {
            'medics': 'Медики',
            'biology': 'Биология',
            'medicine': 'Медицина',
            'psychology': 'Психология',
            'internal_organs': 'Внутренние органы',
            'symptoms': 'Симптомы',
        }
        
        for key, value in categories.items():
            if f'/t/{key}' in url:
                return value
        
        return 'unknown'
    
    def parse_article(self, response):
        """Парсинг статьи"""
        category = response.meta.get('category', 'unknown')
        
        # Заголовок
        title = response.css('h1::text, .title::text').get()
        if not title:
            title = response.css('title::text').get()
        
        if not title:
            self.logger.debug(f"Нет заголовка: {response.url}")
            return
        
        title = title.strip()
        
        # Текст статьи
        text_parts = response.css(
            'article p::text, '
            '.article-content p::text, '
            '.content p::text, '
            '.text p::text, '
            '.entry-content p::text, '
            'p::text'
        ).getall()
        
        text = ' '.join([p.strip() for p in text_parts if p.strip()])
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 150:
            self.logger.debug(f"Слишком короткий текст ({len(text)} символов): {response.url}")
            return
        
        # Год публикации
        year = None
        date_text = response.css('.date::text, time::text').get()
        if date_text:
            year_match = re.search(r'20\d{2}', date_text)
            if year_match:
                year = year_match.group()
        
        item = MedicalArticle()
        item['source'] = 'bigenc'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        self.logger.info(f"Собрана статья [{category}]: {title[:50]}...")
        yield item

