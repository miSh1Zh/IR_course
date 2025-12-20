#include "tokenizer.hpp"
#include <cctype>
#include <algorithm>

bool Tokenizer::is_utf8_start(unsigned char c) {
    return (c & 0xC0) != 0x80;
}

int Tokenizer::utf8_char_length(unsigned char c) {
    if ((c & 0x80) == 0) return 1;      // ASCII
    if ((c & 0xE0) == 0xC0) return 2;   // 2-byte UTF-8
    if ((c & 0xF0) == 0xE0) return 3;   // 3-byte UTF-8
    if ((c & 0xF8) == 0xF0) return 4;   // 4-byte UTF-8
    return 1;  // fallback
}

bool Tokenizer::is_alpha_utf8(const std::string& str, size_t& pos, std::string& char_out) {
    if (pos >= str.size()) return false;
    
    unsigned char c = static_cast<unsigned char>(str[pos]);
    
    // ASCII латиница
    if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z')) {
        char_out = str.substr(pos, 1);
        pos += 1;
        return true;
    }
    
    // UTF-8 кириллица (U+0410-U+044F)
    // В UTF-8: 0xD0 0x90 - 0xD1 0x8F
    if (c == 0xD0 || c == 0xD1) {
        if (pos + 1 < str.size()) {
            unsigned char c2 = static_cast<unsigned char>(str[pos + 1]);
            
            // Кириллические буквы
            if (c == 0xD0 && c2 >= 0x90 && c2 <= 0xBF) {  // А-Я, а-п
                char_out = str.substr(pos, 2);
                pos += 2;
                return true;
            }
            if (c == 0xD1 && c2 >= 0x80 && c2 <= 0x8F) {  // р-я
                char_out = str.substr(pos, 2);
                pos += 2;
                return true;
            }
            // Ё (U+0401) = D0 81, ё (U+0451) = D1 91
            if ((c == 0xD0 && c2 == 0x81) || (c == 0xD1 && c2 == 0x91)) {
                char_out = str.substr(pos, 2);
                pos += 2;
                return true;
            }
        }
    }
    
    // Не буква - пропустить символ
    int len = utf8_char_length(c);
    pos += len;
    return false;
}

std::string Tokenizer::to_lowercase_utf8(const std::string& ch) {
    if (ch.size() == 1) {
        // ASCII
        char c = ch[0];
        if (c >= 'A' && c <= 'Z') {
            return std::string(1, c + 32);
        }
        return ch;
    }
    
    if (ch.size() == 2) {
        unsigned char c1 = static_cast<unsigned char>(ch[0]);
        unsigned char c2 = static_cast<unsigned char>(ch[1]);
        
        // Кириллица: заглавные А-Я (U+0410-U+042F) -> строчные а-я (U+0430-U+044F)
        // А-Я: D0 90 - D0 AF
        // а-я: D0 B0 - D0 BF (а-п) и D1 80 - D1 8F (р-я)
        
        if (c1 == 0xD0) {
            // А-П (U+0410-U+041F) -> а-п (U+0430-U+043F)
            if (c2 >= 0x90 && c2 <= 0x9F) {
                std::string result;
                result += static_cast<char>(0xD0);
                result += static_cast<char>(c2 + 0x20);
                return result;
            }
            // Р-Я (U+0420-U+042F) -> р-я (U+0440-U+044F)
            if (c2 >= 0xA0 && c2 <= 0xAF) {
                std::string result;
                result += static_cast<char>(0xD1);
                result += static_cast<char>(c2 - 0x20);
                return result;
            }
            // Ё (D0 81) -> ё (D1 91)
            if (c2 == 0x81) {
                std::string result;
                result += static_cast<char>(0xD1);
                result += static_cast<char>(0x91);
                return result;
            }
        }
    }
    
    return ch;  // уже строчная или неизвестный символ
}

void Tokenizer::tokenize(const std::string& text, std::vector<std::string>& tokens) {
    std::string current_token;
    size_t pos = 0;
    
    while (pos < text.size()) {
        std::string char_out;
        
        if (is_alpha_utf8(text, pos, char_out)) {
            // Добавить символ к токену в нижнем регистре
            current_token += to_lowercase_utf8(char_out);
        } else {
            // Не буква - завершить токен
            if (!current_token.empty()) {
                tokens.push_back(current_token);
                current_token.clear();
            }
        }
    }
    
    // Добавить последний токен
    if (!current_token.empty()) {
        tokens.push_back(current_token);
    }
}

std::vector<std::string> Tokenizer::tokenize(const std::string& text) {
    std::vector<std::string> tokens;
    tokenize(text, tokens);
    return tokens;
}

