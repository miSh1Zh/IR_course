import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
import re


class BNewsSpider(scrapy.Spider):
    """Spider для сбора статей с b-news.media/science (BIOCAD)
    
    Примечание: сайт использует JavaScript для рендеринга.
    Для полноценной работы требуется Scrapy-Splash.
    Этот spider пытается получить статьи через прямые ссылки.
    """
    
    name = 'bnews'
    allowed_domains = ['b-news.media']
    
    # Известные статьи из раздела /science/
    start_urls = [
        'https://b-news.media',
        'https://b-news.media/science',
        'https://b-news.media/science/malenkij-geroj-kak-myshi-pomogayut-nauke',
        'https://b-news.media/science/movember-pochemu-noyabr-nazyvayut-mesyacem-muzhskogo-zdorovya-i-otrashivaniya-usov',
        'https://b-news.media/science/psoriaz-kak-immunnaya-sistema-atakuet-kozhu',
        'https://b-news.media/science/rozovyj-oktyabr-razvenchivaem-mify-o-rake-molochnoj-zhelezy',
        'https://b-news.media/science/originalnye-vs-vosproizvedennye-preparaty',
        'https://b-news.media/science/artrit-i-budushee-mediciny-ot-obezbolivayushih-k-targetnoj-terapii',
        'https://b-news.media/science/za-chto-vruchili-nobelevskuyu-premiyu-po-medicine-2025',
        'https://b-news.media/science/kak-obespechivaetsya-kachestvo-lekarstvennyh-preparatov',
        'https://b-news.media/science/gennaya-terapiya-kak-nauka-menyaet-nashi-geny-i-lechit-to-chto-kazalos-neizlechimym',
        'https://b-news.media/science/platformennye-preparaty-kak-iz-odnoj-tehnologii-poluchayut-seriyu-lekarstv',
        'https://b-news.media/science/pervye-v-klasse-preparaty-chto-eto-takoe-i-pochemu-za-nimi-budushee',
        'https://b-news.media/science/pochemu-immunnaya-sistema-mozhet-napast-na-sebya',
    ]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 7,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    def parse(self, response):
        """Парсинг страницы"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Если это главная страница раздела - ищем ссылки на статьи
        if response.url.rstrip('/') == 'https://b-news.media/science':
            for link in response.css('a::attr(href)').getall():
                if not link:
                    continue
                full_url = response.urljoin(link)
                if '/science/' in full_url and full_url != 'https://b-news.media/science':
                    yield response.follow(full_url, self.parse_article)
        else:
            # Это статья
            yield from self.parse_article(response)
    
    def parse_article(self, response):
        """Парсинг статьи"""
        
        # Заголовок из meta или h1
        title = response.css('meta[property="og:title"]::attr(content)').get()
        if not title:
            title = response.css('h1::text').get()
        if not title:
            title = response.css('title::text').get()
        
        if not title:
            return
        
        title = title.strip()
        
        # Текст из meta description или body
        text = response.css('meta[property="og:description"]::attr(content)').get()
        if not text:
            text = response.css('meta[name="description"]::attr(content)').get()
        
        # Попробовать извлечь текст из body
        if not text or len(text) < 100:
            text_parts = response.css('article p::text, .content p::text, .post-content p::text, p::text').getall()
            if text_parts:
                text = ' '.join(text_parts).strip()
        
        if not text:
            text = title
        
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) < 50:
            return
        
        # Категория
        category = 'science'
        
        # Год
        year = None
        date_str = response.css('meta[property="article:published_time"]::attr(content)').get()
        if date_str:
            year_match = re.search(r'20\d{2}', date_str)
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
        
        yield item

