#include "stemmer.hpp"
#include <algorithm>

bool Stemmer::is_cyrillic(const std::string& word) {
    if (word.empty()) return false;
    unsigned char c = static_cast<unsigned char>(word[0]);
    return (c == 0xD0 || c == 0xD1);
}

bool Stemmer::ends_with(const std::string& word, const std::string& suffix) {
    if (suffix.size() > word.size()) return false;
    return word.compare(word.size() - suffix.size(), suffix.size(), suffix) == 0;
}

std::string Stemmer::remove_suffix(const std::string& word, const std::string& suffix) {
    if (ends_with(word, suffix)) {
        return word.substr(0, word.size() - suffix.size());
    }
    return word;
}

size_t Stemmer::char_count(const std::string& word) {
    size_t count = 0;
    for (size_t i = 0; i < word.size(); ) {
        unsigned char c = static_cast<unsigned char>(word[i]);
        if ((c & 0x80) == 0) i += 1;
        else if ((c & 0xE0) == 0xC0) i += 2;
        else if ((c & 0xF0) == 0xE0) i += 3;
        else if ((c & 0xF8) == 0xF0) i += 4;
        else i += 1;
        count++;
    }
    return count;
}

std::string Stemmer::stem(const std::string& word) {
    if (word.empty()) return word;
    
    if (is_cyrillic(word)) {
        return stem_russian(word);
    } else {
        return stem_english(word);
    }
}

std::string Stemmer::stem_russian(const std::string& word) {
    // Минимальная длина основы - 2 символа (4 байта в UTF-8 для кириллицы)
    if (word.size() < 4) return word;
    
    std::string result = word;
    
    // Русские окончания (в UTF-8)
    // Окончания существительных, прилагательных, глаголов
    static const std::vector<std::string> endings = {
        // Длинные окончания сначала
        "ивший", "ывший", "ующий", "ающий",  // причастия
        "ённый", "анный", "енный",           // причастия страд.
        "ость", "ести", "ости",              // существительные
        "ами", "ями", "ому", "ему",          // падежные
        "ого", "его", "ых", "их",            // прилагательные
        "ать", "ять", "еть", "ить",          // глаголы инф.
        "ал", "ял", "ел", "ил",              // глаголы прош.
        "ет", "ит", "ат", "ят",              // глаголы наст.
        "ой", "ый", "ий", "ая", "яя",        // прилагательные
        "ов", "ев", "ей",                    // род. падеж мн.
        "ам", "ям", "ом", "ем",              // дат., твор.
        "ах", "ях", "ую", "юю",              // предл., вин.
        "ть", "ся",                          // инфинитив, возвратные
        "а", "я", "о", "е", "и", "ы", "у", "ю" // базовые
    };
    
    // Попробовать удалить окончания (от длинных к коротким)
    for (const auto& ending : endings) {
        if (ends_with(result, ending) && char_count(result) > char_count(ending) + 1) {
            result = remove_suffix(result, ending);
            break;  // Удаляем только одно окончание
        }
    }
    
    return result;
}

std::string Stemmer::stem_english(const std::string& word) {
    // Минимальная длина основы - 2 символа
    if (word.size() < 3) return word;
    
    std::string result = word;
    
    // Шаг 1: Удалить -s, -es
    if (ends_with(result, "sses")) {
        result = remove_suffix(result, "es");
    } else if (ends_with(result, "ies")) {
        result = result.substr(0, result.size() - 3) + "i";
    } else if (ends_with(result, "ss")) {
        // оставить как есть
    } else if (ends_with(result, "s") && result.size() > 3) {
        result = remove_suffix(result, "s");
    }
    
    // Шаг 2: Удалить -ed, -ing
    if (ends_with(result, "eed")) {
        if (result.size() > 4) {
            result = remove_suffix(result, "ed");
        }
    } else if (ends_with(result, "ed") && result.size() > 4) {
        result = remove_suffix(result, "ed");
        // Проверить двойную согласную
        if (result.size() >= 2 && result[result.size()-1] == result[result.size()-2]) {
            result = result.substr(0, result.size() - 1);
        }
    } else if (ends_with(result, "ing") && result.size() > 5) {
        result = remove_suffix(result, "ing");
        // Проверить двойную согласную
        if (result.size() >= 2 && result[result.size()-1] == result[result.size()-2]) {
            result = result.substr(0, result.size() - 1);
        }
    }
    
    // Шаг 3: Заменить -y на -i
    if (ends_with(result, "y") && result.size() > 2) {
        char prev = result[result.size() - 2];
        if (prev != 'a' && prev != 'e' && prev != 'i' && prev != 'o' && prev != 'u') {
            result = result.substr(0, result.size() - 1) + "i";
        }
    }
    
    // Шаг 4: Удалить суффиксы
    static const std::vector<std::string> suffixes = {
        "ational", "ization", "fulness", "ousness", "iveness",
        "ation", "ness", "ment", "able", "ible", "ence", "ance",
        "ful", "ous", "ive", "ize", "ise", "ant", "ent",
        "al", "er", "or", "ly"
    };
    
    for (const auto& suffix : suffixes) {
        if (ends_with(result, suffix) && result.size() > suffix.size() + 2) {
            result = remove_suffix(result, suffix);
            break;
        }
    }
    
    return result;
}

