#ifndef STEMMER_HPP
#define STEMMER_HPP

#include <string>
#include <vector>

/**
 * Класс для стемминга (выделения основы слова)
 * Поддерживает русский и английский языки
 * Упрощённая реализация, основанная на удалении окончаний
 */
class Stemmer {
public:
    /**
     * Получить основу слова
     * @param word - входное слово (в нижнем регистре)
     * @return основа слова
     */
    std::string stem(const std::string& word);
    
private:
    /**
     * Стемминг для русского слова
     */
    std::string stem_russian(const std::string& word);
    
    /**
     * Стемминг для английского слова (Porter Stemmer упрощённый)
     */
    std::string stem_english(const std::string& word);
    
    /**
     * Проверить, является ли слово кириллическим
     */
    bool is_cyrillic(const std::string& word);
    
    /**
     * Проверить, заканчивается ли слово на заданный суффикс
     */
    bool ends_with(const std::string& word, const std::string& suffix);
    
    /**
     * Удалить суффикс из слова
     */
    std::string remove_suffix(const std::string& word, const std::string& suffix);
    
    /**
     * Получить длину слова в символах (UTF-8)
     */
    size_t char_count(const std::string& word);
};

#endif // STEMMER_HPP

