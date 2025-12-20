#ifndef TOKENIZER_HPP
#define TOKENIZER_HPP

#include <string>
#include <vector>

/**
 * Класс для токенизации текста
 * Разбивает текст на слова, приводит к нижнему регистру
 */
class Tokenizer {
public:
    /**
     * Разбить текст на токены
     * @param text - входной текст
     * @param tokens - выходной вектор токенов
     */
    void tokenize(const std::string& text, std::vector<std::string>& tokens);
    
    /**
     * Токенизировать и вернуть вектор
     * @param text - входной текст
     * @return вектор токенов
     */
    std::vector<std::string> tokenize(const std::string& text);
    
private:
    /**
     * Проверить, является ли символ буквой (латиница или кириллица)
     * Учитывает UTF-8 кодировку
     */
    bool is_alpha_utf8(const std::string& str, size_t& pos, std::string& char_out);
    
    /**
     * Привести UTF-8 символ к нижнему регистру
     */
    std::string to_lowercase_utf8(const std::string& ch);
    
    /**
     * Проверить, является ли байт началом UTF-8 символа
     */
    bool is_utf8_start(unsigned char c);
    
    /**
     * Получить длину UTF-8 символа по первому байту
     */
    int utf8_char_length(unsigned char c);
};

#endif // TOKENIZER_HPP

