import scrapy
from medical_crawler.items import MedicalArticle
from datetime import datetime
from urllib.parse import unquote
import re


class WikipediaSpider(scrapy.Spider):
    """Spider для сбора статей с ru.wikipedia.org"""
    
    name = 'wikipedia'
    allowed_domains = ['ru.wikipedia.org']
    
    # Медицинские категории Wikipedia
    start_urls = [
        # Основные разделы медицины
        'https://ru.wikipedia.org/wiki/Категория:Медицина',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания',
        'https://ru.wikipedia.org/wiki/Категория:Симптомы',
        'https://ru.wikipedia.org/wiki/Категория:Медицинская_диагностика',
        'https://ru.wikipedia.org/wiki/Категория:Клиническая_медицина',
        'https://ru.wikipedia.org/wiki/Категория:Доказательная_медицина',
        # Анатомия и физиология
        'https://ru.wikipedia.org/wiki/Категория:Анатомия_человека',
        'https://ru.wikipedia.org/wiki/Категория:Физиология_человека',
        'https://ru.wikipedia.org/wiki/Категория:Гистология',
        'https://ru.wikipedia.org/wiki/Категория:Эмбриология',
        'https://ru.wikipedia.org/wiki/Категория:Патология',
        # Фармакология
        'https://ru.wikipedia.org/wiki/Категория:Фармакология',
        'https://ru.wikipedia.org/wiki/Категория:Лекарственные_средства',
        'https://ru.wikipedia.org/wiki/Категория:Антибиотики',
        'https://ru.wikipedia.org/wiki/Категория:Витамины',
        'https://ru.wikipedia.org/wiki/Категория:Вакцинация',
        # Специальности
        'https://ru.wikipedia.org/wiki/Категория:Хирургия',
        'https://ru.wikipedia.org/wiki/Категория:Нейрохирургия',
        'https://ru.wikipedia.org/wiki/Категория:Терапия',
        'https://ru.wikipedia.org/wiki/Категория:Кардиология',
        'https://ru.wikipedia.org/wiki/Категория:Неврология',
        'https://ru.wikipedia.org/wiki/Категория:Онкология',
        'https://ru.wikipedia.org/wiki/Категория:Психиатрия',
        'https://ru.wikipedia.org/wiki/Категория:Офтальмология',
        'https://ru.wikipedia.org/wiki/Категория:Эндокринология',
        'https://ru.wikipedia.org/wiki/Категория:Гастроэнтерология',
        'https://ru.wikipedia.org/wiki/Категория:Пульмонология',
        'https://ru.wikipedia.org/wiki/Категория:Дерматология',
        'https://ru.wikipedia.org/wiki/Категория:Урология',
        'https://ru.wikipedia.org/wiki/Категория:Гинекология',
        'https://ru.wikipedia.org/wiki/Категория:Акушерство',
        'https://ru.wikipedia.org/wiki/Категория:Педиатрия',
        'https://ru.wikipedia.org/wiki/Категория:Неонатология',
        'https://ru.wikipedia.org/wiki/Категория:Геронтология',
        'https://ru.wikipedia.org/wiki/Категория:Ревматология',
        'https://ru.wikipedia.org/wiki/Категория:Нефрология',
        'https://ru.wikipedia.org/wiki/Категория:Гематология',
        'https://ru.wikipedia.org/wiki/Категория:Иммунология',
        'https://ru.wikipedia.org/wiki/Категория:Аллергология',
        'https://ru.wikipedia.org/wiki/Категория:Травматология',
        'https://ru.wikipedia.org/wiki/Категория:Ортопедия',
        'https://ru.wikipedia.org/wiki/Категория:Оториноларингология',
        'https://ru.wikipedia.org/wiki/Категория:Стоматология',
        'https://ru.wikipedia.org/wiki/Категория:Венерология',
        'https://ru.wikipedia.org/wiki/Категория:Наркология',
        'https://ru.wikipedia.org/wiki/Категория:Токсикология',
        # Интенсивная терапия
        'https://ru.wikipedia.org/wiki/Категория:Реаниматология',
        'https://ru.wikipedia.org/wiki/Категория:Анестезиология',
        'https://ru.wikipedia.org/wiki/Категория:Интенсивная_терапия',
        # Заболевания по системам
        'https://ru.wikipedia.org/wiki/Категория:Инфекционные_заболевания',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания_сердца',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания_печени',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания_почек',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания_лёгких',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания_глаз',
        'https://ru.wikipedia.org/wiki/Категория:Заболевания_нервной_системы',
        'https://ru.wikipedia.org/wiki/Категория:Психические_расстройства',
        'https://ru.wikipedia.org/wiki/Категория:Аутоиммунные_заболевания',
        'https://ru.wikipedia.org/wiki/Категория:Наследственные_болезни',
        'https://ru.wikipedia.org/wiki/Категория:Паразитарные_заболевания',
        'https://ru.wikipedia.org/wiki/Категория:Злокачественные_новообразования',
        # Конкретные заболевания
        'https://ru.wikipedia.org/wiki/Категория:Сахарный_диабет',
        'https://ru.wikipedia.org/wiki/Категория:Инсульт',
        'https://ru.wikipedia.org/wiki/Категория:Инфаркт',
        'https://ru.wikipedia.org/wiki/Категория:Эпилепсия',
        'https://ru.wikipedia.org/wiki/Категория:Бронхиальная_астма',
        'https://ru.wikipedia.org/wiki/Категория:Туберкулёз',
        'https://ru.wikipedia.org/wiki/Категория:ВИЧ-инфекция',
        'https://ru.wikipedia.org/wiki/Категория:Гепатит',
        'https://ru.wikipedia.org/wiki/Категория:Вирусные_инфекции',
        'https://ru.wikipedia.org/wiki/Категория:Бактериальные_инфекции',
        # Дополнительно
        'https://ru.wikipedia.org/wiki/Категория:Радиология',
        'https://ru.wikipedia.org/wiki/Категория:Микробиология',
        'https://ru.wikipedia.org/wiki/Категория:Вирусология',
        'https://ru.wikipedia.org/wiki/Категория:Биохимия',
        'https://ru.wikipedia.org/wiki/Категория:Спортивная_медицина',
        'https://ru.wikipedia.org/wiki/Категория:Реабилитология',
        'https://ru.wikipedia.org/wiki/Категория:Физиотерапия',
        'https://ru.wikipedia.org/wiki/Категория:Диетология',
    ]
    
    custom_settings = {
        'CLOSESPIDER_ITEMCOUNT': 50000,
        'DEPTH_LIMIT': 10,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'ROBOTSTXT_OBEY': True,
        'USER_AGENT': 'MedicalSearchBot/1.0 (Educational project; +https://github.com/example)',
        'JOBDIR': 'logs/wikipedia_state',
    }
    
    def parse(self, response):
        """Парсинг страницы Wikipedia"""
        self.logger.info(f"Парсинг: {response.url}")
        
        # Декодируем URL для проверки (кириллица в URL кодируется)
        decoded_url = unquote(response.url)
        
        # Пропускаем служебные страницы
        skip_patterns = ['Служебная:', 'Обсуждение:', 'Участник:', 'Файл:', 'Шаблон:', 'Портал:', 'Справка:']
        if any(x in decoded_url for x in skip_patterns):
            return
        
        # Если это страница категории — собираем ссылки
        if 'Категория:' in decoded_url or '/wiki/Category:' in response.url:
            self.logger.info(f"Обработка категории: {decoded_url}")
            
            # Статьи в категории
            for link in response.css('#mw-pages a::attr(href)').getall():
                if link and link.startswith('/wiki/') and ':' not in link:
                    yield response.follow(link, self.parse)
            
            # Подкатегории
            for link in response.css('#mw-subcategories a::attr(href)').getall():
                if link and '/wiki/' in link:
                    yield response.follow(link, self.parse)
            
            # Пагинация категории
            next_page = response.css('a:contains("следующая страница")::attr(href)').get()
            if next_page:
                yield response.follow(next_page, self.parse)
        else:
            # Это статья — извлекаем данные
            yield from self.parse_article(response)
    
    def parse_article(self, response):
        """Парсинг статьи Wikipedia"""
        # Заголовок (несколько вариантов селектора)
        title = response.css('#firstHeading span::text').get()
        if not title:
            title = response.css('#firstHeading::text').get()
        if not title:
            title = response.css('h1.firstHeading::text').get()
        if not title:
            title = response.css('h1::text').get()
        
        if not title:
            return
        
        title = title.strip()
        
        # Текст статьи — берём всё
        text_parts = response.css('#mw-content-text .mw-parser-output > p ::text').getall()
        text = ' '.join([t.strip() for t in text_parts if t.strip()])
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[править[^\]]*\]', '', text)
        
        # Минимум 50 символов (очень низкий порог)
        if len(text) < 50:
            return
        
        # Категория (первая из списка)
        categories = response.css('#mw-normal-catlinks a::text').getall()
        category = categories[0] if categories else 'Wikipedia'
        
        item = MedicalArticle()
        item['source'] = 'wikipedia'
        item['url'] = response.url
        item['title'] = title
        item['text'] = text
        item['category'] = category
        item['year'] = None
        item['crawled_at'] = datetime.now().isoformat()
        
        self.logger.info(f"Собрана статья: {title[:50]}...")
        yield item

