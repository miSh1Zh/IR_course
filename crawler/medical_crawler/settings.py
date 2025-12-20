import os

BOT_NAME = 'medical_crawler'
SPIDER_MODULES = ['medical_crawler.spiders']
NEWSPIDER_MODULE = 'medical_crawler.spiders'

# Вежливый краулинг
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS = 8

USER_AGENT = 'Medical Research Bot (+misha.zhadnov@student.ru)'

# MongoDB URI (из Docker environment)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

# Pipelines
ITEM_PIPELINES = {
    'medical_crawler.pipelines.MongoDBPipeline': 300,
}

# Логирование
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/scrapy.log'

# Retry
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Таймауты
DOWNLOAD_TIMEOUT = 30

# Отключить телеметрию
TELNETCONSOLE_ENABLED = False

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# Twisted reactor
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Feed export encoding
FEED_EXPORT_ENCODING = "utf-8"

