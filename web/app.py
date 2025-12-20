#!/usr/bin/env python3
"""
Flask веб-интерфейс для медицинской поисковой системы
"""

import os
import subprocess
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Конфигурация
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
SEARCHER_PATH = os.getenv('SEARCHER_PATH', '../engine/searcher')
INDEX_PATH = os.getenv('INDEX_PATH', '../data/index.bin')


def get_search_results(query, limit=50):
    """Выполнить поиск через C++ searcher"""
    try:
        result = subprocess.run(
            [SEARCHER_PATH, f'--index={INDEX_PATH}', f'--query={query}', f'--limit={limit}'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Парсинг результатов
        lines = result.stdout.strip().split('\n')
        documents = []
        total = 0
        
        for line in lines:
            if 'Найдено:' in line:
                try:
                    total = int(line.split(':')[1].strip().split()[0])
                except:
                    pass
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                # Заголовок документа
                title = line.split('.', 1)[1].strip() if '.' in line else line
                documents.append({'title': title, 'url': '', 'category': ''})
            elif line.strip().startswith('http'):
                # URL
                if documents:
                    documents[-1]['url'] = line.strip()
            elif line.strip().startswith('[') and line.strip().endswith(']'):
                # Категория
                if documents:
                    documents[-1]['category'] = line.strip()[1:-1]
        
        return {'total': total, 'documents': documents}
        
    except subprocess.TimeoutExpired:
        return {'error': 'Timeout', 'total': 0, 'documents': []}
    except FileNotFoundError:
        return {'error': 'Searcher not found', 'total': 0, 'documents': []}
    except Exception as e:
        return {'error': str(e), 'total': 0, 'documents': []}


def get_corpus_stats():
    """Получить статистику корпуса из MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client['medical_search']
        articles = db['articles']
        
        stats = {
            'total_docs': articles.count_documents({}),
            'sources': articles.distinct('source'),
            'categories': len(articles.distinct('category'))
        }
        
        client.close()
        return stats
    except Exception as e:
        return {'error': str(e)}


@app.route('/')
def index():
    """Главная страница с формой поиска"""
    stats = get_corpus_stats()
    return render_template('search.html', stats=stats)


@app.route('/search')
def search():
    """Страница результатов поиска"""
    query = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))
    limit = 50
    
    if not query:
        return render_template('search.html', stats=get_corpus_stats())
    
    results = get_search_results(query, limit=limit)
    
    return render_template('results.html', 
                         query=query, 
                         results=results,
                         page=page,
                         limit=limit)


@app.route('/api/search')
def api_search():
    """API endpoint для поиска (JSON)"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 50))
    
    if not query:
        return jsonify({'error': 'Query is required', 'documents': []})
    
    results = get_search_results(query, limit=limit)
    return jsonify(results)


@app.route('/api/stats')
def api_stats():
    """API endpoint для статистики"""
    return jsonify(get_corpus_stats())


if __name__ == '__main__':
    # Проверить наличие searcher
    if not os.path.exists(SEARCHER_PATH):
        print(f"Searcher не найден: {SEARCHER_PATH}")
        print("Соберите его командой: cd engine && make searcher")
    
    if not os.path.exists(INDEX_PATH):
        print(f"Индекс не найден: {INDEX_PATH}")
        print("Создайте его командой: ./scripts/build_index.sh")
    
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    print(f"Запуск сервера на http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

