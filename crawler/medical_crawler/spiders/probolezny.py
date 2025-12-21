import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class ProboleznySpider(scrapy.Spider):
    """Spider для сбора статей с probolezny.ru
    
    Энциклопедия заболеваний, составленная практикующими врачами.
    Статьи по различным категориям болезней.
    """
    
    name = 'probolezny'
    allowed_domains = ['probolezny.ru', 'www.probolezny.ru']
    
    start_urls = ['https://probolezny.ru/']
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 6,
        'DOWNLOAD_DELAY': 3,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'JOBDIR': '/app/logs/probolezny_state',
    }
    
    def parse(self, response):
        """Парсинг главной страницы и категорий"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Ссылки на статьи и категории
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            # Статьи имеют структуру /diseases/... или /bolezni/...
            if 'probolezny.ru' in full_url and full_url != 'https://probolezny.ru/':
                # Пропускаем служебные страницы
                skip_patterns = ['/author/', '/clinic/', '/doctor/', '/user/', '/login', '/register']
                if any(pattern in full_url for pattern in skip_patterns):
                    continue
                
                # Следуем по ссылкам
                yield response.follow(full_url, self.parse_page)
    
    def parse_page(self, response):
        """Парсинг страницы - может быть категорией или статьей"""
        # Проверяем, есть ли на странице контент статьи
        has_article_content = response.css('article, .article-content, h1').get()
        
        if has_article_content:
            # Это статья
            yield from self.parse_article(response)
        
        # В любом случае, ищем ссылки на другие статьи
        for link in response.css('a::attr(href)').getall():
            if link and 'probolezny.ru' in response.urljoin(link):
                full_url = response.urljoin(link)
                skip_patterns = ['/author/', '/clinic/', '/doctor/', '/user/', '/login', '/register']
                if not any(pattern in full_url for pattern in skip_patterns):
                    yield response.follow(full_url, self.parse_page)
    
    def parse_article(self, response):
        """Парсинг статьи"""
        # Заголовок
        title = response.css('h1::text').get()
        if not title:
            title = response.css('title::text').get()
        
        if not title:
            return
        
        title = title.strip()
        
        # Текст статьи
        text_parts = response.css(
            'article p::text, '
            '.article-content p::text, '
            '.content p::text, '
            '.disease-content p::text, '
            'p::text'
        ).getall()
        
        text = ' '.join([p.strip() for p in text_parts if p.strip()])
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 150:
            return
        
        # Категория
        category = response.css('.category::text, .tag::text, .specialty::text').get()
        if category:
            category = category.strip()
        
        # Год
        year = None
        date_text = response.css('.date::text, time::text, .published::text').get()
        if date_text:
            year_match = re.search(r'20\d{2}', date_text)
            if year_match:
                year = year_match.group()
        
        item = MedicalArticle()
        item['source'] = 'probolezny'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        self.logger.info(f"Собрана статья: {title[:50]}...")
        yield item

