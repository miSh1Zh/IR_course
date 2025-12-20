import scrapy


class MedicalArticle(scrapy.Item):
    """Структура медицинской статьи для хранения в MongoDB"""
    source = scrapy.Field()      # 'journaldoctor', 'source2', 'source3'
    url = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()        # Полный текст
    category = scrapy.Field()
    year = scrapy.Field()
    crawled_at = scrapy.Field()

