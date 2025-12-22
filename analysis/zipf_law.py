#!/usr/bin/env python3
"""
Анализ закона Ципфа для корпуса документов.

Закон Ципфа: f(r) = C / r^alpha
- f(r) - частота слова с рангом r
- r - ранг (1 = самое частое)
- alpha ~ 1.0 для естественного языка
- C - константа пропорциональности
"""
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import sys
from collections import Counter


def tokenize_simple(text):
    """Простая токенизация для анализа Ципфа."""
    if not text:
        return []
    text = text.lower()
    tokens = re.findall(r'[а-яёa-z]+', text)
    return [t for t in tokens if len(t) >= 2]


def read_from_mongodb(mongo_uri):
    """
    Читает корпус из MongoDB и считает частоту слов (TF).
    
    Args:
        mongo_uri: URI подключения к MongoDB
    
    Returns:
        список (term, frequency) по убыванию частоты
    """
    from pymongo import MongoClient
    
    client = MongoClient(mongo_uri)
    try:
        db = client.get_default_database()
    except:
        db = client['medical_search']
    collection = db['articles']
    
    doc_count = collection.count_documents({})
    print(f"Документов в MongoDB: {doc_count}")
    
    word_counts = Counter()
    processed = 0
    
    for doc in collection.find({}, {'text': 1, 'title': 1}):
        text = (doc.get('text', '') or '') + ' ' + (doc.get('title', '') or '')
        tokens = tokenize_simple(text)
        word_counts.update(tokens)
        processed += 1
        
        if processed % 1000 == 0:
            print(f"\rОбработано: {processed}/{doc_count}", end='', flush=True)
    
    print(f"\rОбработано: {processed}/{doc_count}")
    print(f"Уникальных слов: {len(word_counts)}")
    print(f"Всего слов: {sum(word_counts.values())}")
    
    client.close()
    return word_counts.most_common()


def analyze_zipf(terms, output_dir='.'):
    """
    Анализ закона Ципфа.
    
    Параметры вычисляются методом линейной регрессии в логарифмическом пространстве:
    log(f) = log(C) - alpha*log(r)
    
    Где:
    - f - частота слова
    - r - ранг слова
    - alpha - показатель степени (~1.0 для естественного языка)
    - C - константа
    """
    sorted_terms = sorted(terms, key=lambda x: x[1], reverse=True)
    
    ranks = np.array(range(1, len(sorted_terms) + 1))
    frequencies = np.array([t[1] for t in sorted_terms])
    
    mask = frequencies > 0
    ranks = ranks[mask]
    frequencies = frequencies[mask]
    
    log_ranks = np.log(ranks)
    log_freqs = np.log(frequencies)
    
    coeffs = np.polyfit(log_ranks, log_freqs, 1)
    alpha = -coeffs[0]
    C = np.exp(coeffs[1])
    
    predicted = coeffs[1] + coeffs[0] * log_ranks
    ss_res = np.sum((log_freqs - predicted) ** 2)
    ss_tot = np.sum((log_freqs - np.mean(log_freqs)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    # Теоретическая кривая
    theoretical = C / np.power(ranks, alpha)
    
    # График (один, как по заданию)
    freq_label = 'Частота'
    
    plt.figure(figsize=(10, 6))
    plt.loglog(ranks, frequencies, 'b.', markersize=1, alpha=0.5, label='Данные')
    plt.loglog(ranks, theoretical, 'r-', linewidth=2, 
               label=f'Закон Ципфа: f(r) = {C:.0f}/r^{alpha:.2f}')
    plt.xlabel('Ранг (log)')
    plt.ylabel(f'{freq_label} (log)')
    plt.title(f'Закон Ципфа (alpha = {alpha:.2f})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'zipf_law.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nГрафик сохранен: {output_file}")
    
    # Статистика
    print(f"Уникальных термов: {len(sorted_terms)}")
    print(f"Максимальная частота: {max(frequencies)}")
    print(f"Минимальная частота: {min(frequencies)}")
    print(f"Средняя частота: {np.mean(frequencies):.2f}")
    print(f"Медианная частота: {np.median(frequencies):.2f}")
    
    hapax = sum(1 for f in frequencies if f == 1)
    print(f"Hapax legomena (f=1): {hapax} ({100*hapax/len(sorted_terms):.1f}%)")
    
    print(f"\nТоп-20 термов:")
    for i, (term, freq) in enumerate(sorted_terms[:20]):
        print(f"  {i+1:2d}. {term:30s} {freq:6d}")
    
    # Сохранение частот
    freq_file = os.path.join(output_dir, 'term_frequencies.txt')
    with open(freq_file, 'w', encoding='utf-8') as f:
        f.write("rank\tterm\tfrequency\n")
        for rank, (term, freq) in enumerate(sorted_terms, 1):
            f.write(f"{rank}\t{term}\t{freq}\n")
    print(f"Частоты сохранены: {freq_file}")
    
    return alpha, C, r_squared


def main():
    """
    Анализ закона Ципфа по корпусу из MongoDB.
    
    Переменные окружения:
        MONGO_URI - URI подключения к MongoDB (по умолчанию mongodb://localhost:27017/medical_search)
    """
    mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/medical_search')
    output_dir = '.'
    
    # Парсинг аргументов
    for arg in sys.argv[1:]:
        if arg.startswith('--mongo='):
            mongo_uri = arg.split('=', 1)[1]
        elif arg.startswith('--output='):
            output_dir = arg.split('=', 1)[1]
        elif arg in ['-h', '--help']:
            print("Использование: python zipf_law.py [--mongo=URI] [--output=DIR]")
            print("По умолчанию читает из MongoDB (MONGO_URI)")
            return
    
    print("Анализ закона Ципфа")
    print(f"MongoDB: {mongo_uri}")
    
    terms = read_from_mongodb(mongo_uri)
    if not terms:
        print("Ошибка: не удалось прочитать корпус из MongoDB")
        return
    
    alpha, C, r2 = analyze_zipf(terms, output_dir)
    

    
    print(f"\nВывод:")
    print(f"Закон Ципфа: f(r) = C / r^alpha")
    print(f"  alpha = {alpha:.4f}")
    print(f"  C = {C:.2f}")
    print(f"  R^2 = {r2:.4f}")
    
    if 0.8 <= alpha <= 1.2:
        print(f"Распределение ХОРОШО соответствует закону Ципфа (alpha ~ 1.0)")
    elif 0.5 <= alpha <= 1.5:
        print(f"Распределение ЧАСТИЧНО соответствует закону Ципфа")
    else:
        print(f"Распределение ОТКЛОНЯЕТСЯ от закона Ципфа")
    
    try:
        plt.show()
    except:
        pass


if __name__ == "__main__":
    main()

