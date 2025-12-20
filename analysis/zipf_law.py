#!/usr/bin/env python3
import struct
import matplotlib.pyplot as plt
import numpy as np
import os
import sys


def read_index_terms(index_file):
    terms = []
    
    with open(index_file, 'rb') as f:
        magic = struct.unpack('I', f.read(4))[0]
        
        if magic != 0x5849444D:
            print(f"Ошибка: неверный формат файла (magic={hex(magic)})")
            return []
        
        version = struct.unpack('I', f.read(4))[0]
        num_terms = struct.unpack('I', f.read(4))[0]
        num_docs = struct.unpack('I', f.read(4))[0]
        forward_offset = struct.unpack('Q', f.read(8))[0]
        reserved = struct.unpack('Q', f.read(8))[0]
        
        print(f"Версия индекса: {version}")
        print(f"Документов: {num_docs}")
        print(f"Термов: {num_terms}")
        
        for i in range(num_terms):
            term_len = struct.unpack('I', f.read(4))[0]
            term = f.read(term_len).decode('utf-8')
            posting_len = struct.unpack('I', f.read(4))[0]
            f.seek(posting_len * 4, 1)
            
            terms.append((term, posting_len))
            
            if (i + 1) % 10000 == 0:
                print(f"\rПрочитано термов: {i + 1}/{num_terms}", end='', flush=True)
    
    print(f"\rПрочитано термов: {num_terms}/{num_terms}")
    
    return terms


def analyze_zipf(terms, output_dir='.'):
    sorted_terms = sorted(terms, key=lambda x: x[1], reverse=True)
    
    ranks = list(range(1, len(sorted_terms) + 1))
    frequencies = [t[1] for t in sorted_terms]
    
    log_ranks = np.log(ranks)
    log_freqs = np.log(frequencies)
    
    coeffs = np.polyfit(log_ranks, log_freqs, 1)
    alpha = -coeffs[0]
    C = np.exp(coeffs[1])
    
    print(f"\nПараметры закона Ципфа:")
    print(f"  α (показатель степени) = {alpha:.4f}")
    print(f"  C (константа) = {C:.2f}")
    print(f"  Теоретическое значение α ≈ 1.0")
    
    theoretical = C / np.power(ranks, alpha)
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.loglog(ranks, frequencies, 'b.', markersize=1, alpha=0.5, label='Данные')
    plt.loglog(ranks, theoretical, 'r-', linewidth=2, 
               label=f'Закон Ципфа (α={alpha:.2f})')
    plt.xlabel('Ранг (log)')
    plt.ylabel('Частота (log)')
    plt.title('Закон Ципфа: log(rank) vs log(frequency)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    top_n = min(50, len(sorted_terms))
    top_terms = [t[0] for t in sorted_terms[:top_n]]
    top_freqs = [t[1] for t in sorted_terms[:top_n]]
    
    y_pos = list(range(top_n))
    plt.barh(y_pos, top_freqs, color='steelblue')
    plt.yticks(y_pos, top_terms, fontsize=8)
    plt.xlabel('Частота (количество документов)')
    plt.title(f'Топ-{top_n} самых частых термов')
    plt.gca().invert_yaxis()
    
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'zipf_law.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nГрафик сохранен в {output_file}")
    
    print(f"\nВсего уникальных термов: {len(terms)}")
    print(f"Максимальная частота: {max(frequencies)}")
    print(f"Минимальная частота: {min(frequencies)}")
    print(f"Средняя частота: {np.mean(frequencies):.2f}")
    print(f"Медианная частота: {np.median(frequencies):.2f}")
    
    hapax = sum(1 for f in frequencies if f == 1)
    print(f"Hapax legomena (частота=1): {hapax} ({100*hapax/len(terms):.1f}%)")
    
    print("\nТоп-20 термов:")
    for i, (term, freq) in enumerate(sorted_terms[:20]):
        print(f"  {i+1:2d}. {term:30s} {freq:6d}")
    
    with open(os.path.join(output_dir, 'term_frequencies.txt'), 'w', encoding='utf-8') as f:
        f.write("rank\tterm\tfrequency\n")
        for rank, (term, freq) in enumerate(sorted_terms, 1):
            f.write(f"{rank}\t{term}\t{freq}\n")
    
    print(f"Частоты сохранены в {output_dir}/term_frequencies.txt")
    
    return alpha, C


def main():
    if len(sys.argv) > 1:
        index_file = sys.argv[1]
    else:
        index_file = '../data/index.bin'
    
    if not os.path.exists(index_file):
        print(f"Ошибка: файл индекса не найден: {index_file}")
        print("Использование: python zipf_law.py [путь_к_index.bin]")
        return
    
    print(f"Анализ закона Ципфа")
    print(f"Файл индекса: {index_file}\n")
    
    terms = read_index_terms(index_file)
    
    if not terms:
        print("Ошибка: не удалось прочитать термы из индекса")
        return
    
    alpha, C = analyze_zipf(terms)
    
    print(f"\nВывод:")
    if 0.8 <= alpha <= 1.2:
        print(f"Распределение хорошо соответствует закону Ципфа (α={alpha:.2f} ≈ 1)")
    elif 0.5 <= alpha <= 1.5:
        print(f"Распределение частично соответствует закону Ципфа (α={alpha:.2f})")
    else:
        print(f"Распределение отклоняется от закона Ципфа (α={alpha:.2f})")
    
    plt.show()


if __name__ == "__main__":
    main()

