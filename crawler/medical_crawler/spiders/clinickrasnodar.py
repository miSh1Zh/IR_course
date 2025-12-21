import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class ClinicKrasnodarSpider(scrapy.Spider):
    """Spider для сбора статей с клиникакраснодар.рф
    
    Медицинская клиника, статьи в разделе /articles/
    """
    
    name = 'clinickrasnodar'
    allowed_domains = ['xn--80ahbdcbmjcgaeqocq5cyc.xn--p1ai', 'клиникакраснодар.рф']
    
    start_urls = [
        'https://xn--80ahbdcbmjcgaeqocq5cyc.xn--p1ai/articles/',  # Punycode для клиникакраснодар.рф
    ]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 5,
        'DOWNLOAD_DELAY': 4,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'JOBDIR': '/app/logs/clinickrasnodar_state',
    }
    
    def parse(self, response):
        """Парсинг списка статей"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Ссылки на статьи
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            # Статьи в разделе /articles/
            if '/articles/' in full_url and full_url.count('/') > full_url.count('/articles/'):
                yield response.follow(full_url, self.parse_article)
        
        # Пагинация
        next_page = response.css('a.next::attr(href), .pagination a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
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

