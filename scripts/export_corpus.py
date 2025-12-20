#!/usr/bin/env python3
import os
from pymongo import MongoClient
import json

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')

def export_corpus(output_file='../data/corpus.json'):
    client = MongoClient(MONGO_URI)
    db = client['medical_search']
    articles = db['articles']
    
    total = articles.count_documents({})
    print(f"Экспорт {total} документов в NDJSON...")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, doc in enumerate(articles.find(), 1):
            doc.pop('_id', None)
            f.write(json.dumps(doc, ensure_ascii=False) + '\n')
            
            if i % 1000 == 0:
                print(f"\rЭкспортировано: {i}/{total}", end='', flush=True)
    
    print(f"\nГотово: {output_file}")
    client.close()

if __name__ == "__main__":
    export_corpus()

