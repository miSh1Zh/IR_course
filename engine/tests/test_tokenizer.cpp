#include <iostream>
#include <cassert>
#include "../src/tokenizer.hpp"

void test_simple() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("Hello world");
    
    assert(tokens.size() == 2);
    assert(tokens[0] == "hello");
    assert(tokens[1] == "world");
    std::cout << " test_simple" << std::endl;
}

void test_russian() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("Привет мир");
    
    assert(tokens.size() == 2);
    assert(tokens[0] == "привет");
    assert(tokens[1] == "мир");
    std::cout << " test_russian" << std::endl;
}

void test_mixed() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("Hello Привет");
    
    assert(tokens.size() == 2);
    std::cout << " test_mixed" << std::endl;
}

int main() {
    std::cout << "=== Тесты токенизатора ===" << std::endl;
    test_simple();
    test_russian();
    test_mixed();
    std::cout << "Все тесты пройдены!" << std::endl;
    return 0;
}

