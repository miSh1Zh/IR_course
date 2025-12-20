from pymongo import MongoClient


class MongoDBPipeline:
    def open_spider(self, spider):
        mongo_uri = spider.settings.get('MONGO_URI', 'mongodb://localhost:27017/')
        self.client = MongoClient(mongo_uri)
        self.db = self.client['medical_search']
        self.collection = self.db['articles']
        
        self.collection.create_index('url', unique=True)
        self.collection.create_index([('source', 1), ('title', 1)])
        
        spider.logger.info(f"Подключено к MongoDB: {mongo_uri}")
        spider.logger.info(f"Текущее количество документов: {self.collection.count_documents({})}")
    
    def close_spider(self, spider):
        total = self.collection.count_documents({})
        spider.logger.info(f"Закрыто. Всего в БД: {total}")
        self.client.close()
    
    def process_item(self, item, spider):
        if not item.get('title') or not item.get('text'):
            spider.logger.debug(f"Пропущено (нет title/text): {item.get('url')}")
            return item
        
        if len(item['text']) < 100:
            spider.logger.debug(f"Пропущено (короткий текст): {item.get('url')}")
            return item
        
        try:
            self.collection.insert_one(dict(item))
            spider.logger.info(f"Сохранено: {item['title'][:50]}...")
        except Exception as e:
            spider.logger.debug(f"Пропущено ({e}): {item.get('url')}")
        
        return item

