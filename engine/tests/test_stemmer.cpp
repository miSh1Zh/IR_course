#include <iostream>
#include <cassert>
#include "../src/stemmer.hpp"

void test_english() {
    Stemmer stemmer;
    
    std::string s1 = stemmer.stem("running");
    std::string s2 = stemmer.stem("runs");
    std::cout << "running -> " << s1 << ", runs -> " << s2 << std::endl;
    
    // Базовая проверка что стемминг что-то делает
    assert(!s1.empty());
    assert(!s2.empty());
    std::cout << " test_english" << std::endl;
}

void test_russian() {
    Stemmer stemmer;
    
    std::string s1 = stemmer.stem("кардиология");
    std::string s2 = stemmer.stem("кардиологии");
    std::cout << "кардиология -> " << s1 << std::endl;
    std::cout << "кардиологии -> " << s2 << std::endl;
    
    assert(!s1.empty());
    assert(!s2.empty());
    std::cout << " test_russian" << std::endl;
}

int main() {
    std::cout << "=== Тесты стемминга ===" << std::endl;
    test_english();
    test_russian();
    std::cout << "Все тесты пройдены!" << std::endl;
    return 0;
}

