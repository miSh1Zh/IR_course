#!/usr/bin/env python3
import os
from pymongo import MongoClient
import json

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')


def main():
    try:
        client = MongoClient(MONGO_URI)
        db = client['medical_search']
        articles = db['articles']
    except Exception as e:
        print(f"Ошибка подключения к MongoDB: {e}")
        return
    
    total_docs = articles.count_documents({})
    
    if total_docs == 0:
        print("Корпус пуст. Запустите краулер для сбора документов.")
        client.close()
        return
    
    stats = db.command("collstats", "articles")
    raw_size_mb = stats.get('size', 0) / (1024 * 1024)
    
    print(f"1. Количество документов: {total_docs}")
    
    pipeline = [
        {"$project": {
            "text_length": {"$strLenCP": {"$ifNull": ["$text", ""]}},
            "title_length": {"$strLenCP": {"$ifNull": ["$title", ""]}}
        }},
        {"$group": {
            "_id": None,
            "avg_text": {"$avg": "$text_length"},
            "total_text": {"$sum": "$text_length"}
        }}
    ]
    
    result = list(articles.aggregate(pipeline))
    
    if result:
        text_stats = result[0]
        total_text_mb = text_stats['total_text'] / (1024 * 1024)
        avg_text_chars = text_stats['avg_text']
        avg_text_kb = avg_text_chars / 1024
        
        print(f"2. Размер «сырых» данных: {raw_size_mb:.2f} МБ")
        print(f"3. Размер выделенного текста: {total_text_mb:.2f} МБ")
        print(f"4. Средний размер текста в документе: {avg_text_chars:.0f} символов ({avg_text_kb:.1f} КБ)")
    
    sources = articles.distinct('source')
    print(f"Источники: {', '.join(sources)}")
    
    stats_data = {
        'total_docs': total_docs,
        'raw_size_mb': round(raw_size_mb, 2),
        'text_size_mb': round(total_text_mb, 2) if result else 0,
        'avg_text_chars': round(avg_text_chars, 0) if result else 0,
        'sources': sources
    }
    
    with open('corpus_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)
    
    print("Статистика сохранена в corpus_stats.json")
    
    client.close()


if __name__ == "__main__":
    main()
