import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class BNewsSpider(scrapy.Spider):
    """Spider для сбора статей с b-news.media (BIOCAD)"""
    
    name = 'bnews'
    allowed_domains = ['b-news.media']
    
    # Все основные разделы сайта
    start_urls = [
        'https://b-news.media/science',
        'https://b-news.media/news',
        'https://b-news.media/techno',
        'https://b-news.media/life',
        'https://b-news.media/career',
        'https://b-news.media/special',
    ]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 7,
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'JOBDIR': 'logs/bnews_state',
    }
    
    def parse(self, response):
        """Парсинг страницы раздела"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Извлекаем категорию из URL
        category = self._extract_category(response.url)
        
        # Ищем все ссылки на статьи
        for link in response.css('a::attr(href)').getall():
            if not link:
                continue
            
            full_url = response.urljoin(link)
            
            # Проверяем, что это ссылка на статью из нужного раздела
            if self._is_article_url(full_url, category):
                yield response.follow(full_url, self.parse_article, meta={'category': category})
        
        # Кнопка "Загрузить еще" или пагинация
        load_more = response.css('button.load-more::attr(data-page)').get()
        if load_more:
            self.logger.info(f"Найдена пагинация: страница {load_more}")
    
    def _extract_category(self, url):
        """Извлечь категорию из URL"""
        for cat in ['science', 'news', 'techno', 'life', 'career', 'special']:
            if f'/{cat}' in url:
                return cat
        return 'unknown'
    
    def _is_article_url(self, url, category):
        """Проверить, что URL ведет на статью"""
        # Статья имеет вид: /category/article-slug
        pattern = f'/{category}/[a-z0-9-]+'
        return bool(re.search(pattern, url)) and url.count('/') >= 4
    
    def parse_article(self, response):
        """Парсинг статьи"""
        category = response.meta.get('category', 'unknown')
        
        # Заголовок
        title = response.css('meta[property="og:title"]::attr(content)').get()
        if not title:
            title = response.css('h1::text, h2.article-title::text').get()
        if not title:
            title = response.css('title::text').get()
        
        if not title:
            self.logger.debug(f"Нет заголовка: {response.url}")
            return
        
        # Убираем префикс "B—News — " если есть
        title = title.replace('B—News — ', '').replace('B-News — ', '').strip()
        
        # Текст статьи
        text = None
        
        # 1. Попытка извлечь из meta description
        text = response.css('meta[property="og:description"]::attr(content)').get()
        if not text:
            text = response.css('meta[name="description"]::attr(content)').get()
        
        # 2. Извлечь полный текст из body
        if not text or len(text) < 200:
            # Попробовать различные селекторы для контента
            text_parts = response.css(
                'article p::text, '
                '.article-content p::text, '
                '.post-content p::text, '
                '.content p::text, '
                'main p::text'
            ).getall()
            
            if text_parts:
                text = ' '.join([p.strip() for p in text_parts if p.strip()])
        
        if not text:
            text = title
        
        # Очистка текста
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 50:
            self.logger.debug(f"Слишком короткий текст ({len(text)} символов): {response.url}")
            return
        
        # Год публикации
        year = None
        date_str = response.css('meta[property="article:published_time"]::attr(content)').get()
        if not date_str:
            date_str = response.css('time::attr(datetime)').get()
        
        if date_str:
            # Попробовать извлечь год
            year_match = re.search(r'20\d{2}', date_str)
            if year_match:
                year = year_match.group()
        
        # Если год не найден, попробовать из текста даты
        if not year:
            date_text = response.css('.date::text, time::text').get()
            if date_text:
                year_match = re.search(r'20\d{2}', date_text)
                if year_match:
                    year = year_match.group()
        
        item = MedicalArticle()
        item['source'] = 'bnews'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = year
        item['crawled_at'] = datetime.now().isoformat()
        
        self.logger.info(f"Собрана статья [{category}]: {title[:50]}...")
        yield item
