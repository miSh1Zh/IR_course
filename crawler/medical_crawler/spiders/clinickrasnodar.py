import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class ClinicKrasnodarSpider(scrapy.Spider):
    """Spider для сбора статей с клиникакраснодар.рф
    
    Медицинская клиника, статьи в разделе /articles/
    """
    
    name = 'clinickrasnodar'
    allowed_domains = ['xn--80aaapramcbfxfnzfl.xn--p1ai', 'клиникакраснодар.рф']
    
    start_urls = [
        'https://xn--80aaapramcbfxfnzfl.xn--p1ai/articles/',  # Правильный Punycode для клиникакраснодар.рф
    ]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 6,
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        },
        'COOKIES_ENABLED': True,
        'JOBDIR': 'logs/clinickrasnodar_state',
    }
    
    def parse(self, response):
        """Парсинг списка статей"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Ссылки на статьи
        # Структура: /articles/stati-patsientam/{slug}/
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            # Статьи в разделе /articles/
            if '/articles/' in full_url:
                # Извлекаем путь после /articles/
                path_after = full_url.split('/articles/')[-1].strip('/')
                parts = [p for p in path_after.split('/') if p]
                
                # Статья: /articles/category/slug/ (2+ части)
                if len(parts) >= 2:
                    yield response.follow(full_url, self.parse_article)
                # Категория: /articles/category/ (1 часть) — обходим дальше
                elif len(parts) == 1:
                    yield response.follow(full_url, self.parse)
        
        # Пагинация (PAGEN_1=2 и т.д.)
        next_page = response.css('link[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
        
        # Другие варианты пагинации
        for page_link in response.css(
            'a.next::attr(href), '
            '.pagination a::attr(href), '
            'a[rel="next"]::attr(href)'
        ).getall():
            if page_link and 'PAGEN' in page_link:
                yield response.follow(page_link, self.parse)
    
    def parse_article(self, response):
        """Парсинг статьи"""
        # Заголовок
        title = response.css('h1::text, .article-title::text').get()
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
            'p::text'
        ).getall()
        
        text = ' '.join([p.strip() for p in text_parts if p.strip()])
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 100:
            self.logger.debug(f"Слишком короткий текст ({len(text)} символов): {response.url}")
            return
        
        # Категория
        category = response.css('.category::text, .tag::text, .specialty::text').get()
        if category:
            category = category.strip()
        
        # Год
        year = None
        date_text = response.css('.date::text, time::text').get()
        if date_text:
            year_match = re.search(r'20\d{2}', date_text)
            if year_match:
                year = year_match.group()
        
        item = MedicalArticle()
        item['source'] = 'clinickrasnodar'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        self.logger.info(f"Собрана статья: {title[:50]}...")
        yield item

