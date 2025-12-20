#include <iostream>
#include <cassert>
#include <vector>
#include <string>
#include "../src/tokenizer.hpp"
#include "../src/stemmer.hpp"
#include "../src/hashmap.hpp"
#include "../src/indexer.hpp"
#include "../src/searcher.hpp"
#include "../src/query_parser.hpp"

// ========== Тесты токенизатора ==========

void test_tokenizer_simple() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("Hello world");
    
    assert(tokens.size() == 2);
    assert(tokens[0] == "hello");
    assert(tokens[1] == "world");
    std::cout << "test_tokenizer_simple" << std::endl;
}

void test_tokenizer_punctuation() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("Hello, world! How are you?");
    
    assert(tokens.size() == 5);
    assert(tokens[0] == "hello");
    assert(tokens[1] == "world");
    assert(tokens[2] == "how");
    assert(tokens[3] == "are");
    assert(tokens[4] == "you");
    std::cout << " test_tokenizer_punctuation" << std::endl;
}

void test_tokenizer_russian() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("Привет мир");
    
    assert(tokens.size() == 2);
    assert(tokens[0] == "привет");
    assert(tokens[1] == "мир");
    std::cout << " test_tokenizer_russian" << std::endl;
}

void test_tokenizer_mixed() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("Hello Привет World Мир");
    
    assert(tokens.size() == 4);
    assert(tokens[0] == "hello");
    assert(tokens[1] == "привет");
    assert(tokens[2] == "world");
    assert(tokens[3] == "мир");
    std::cout << " test_tokenizer_mixed" << std::endl;
}

void test_tokenizer_empty() {
    Tokenizer tok;
    std::vector<std::string> tokens = tok.tokenize("");
    assert(tokens.size() == 0);
    
    tokens = tok.tokenize("   ");
    assert(tokens.size() == 0);
    
    tokens = tok.tokenize("123 456");  // Цифры без букв
    assert(tokens.size() == 0);
    std::cout << " test_tokenizer_empty" << std::endl;
}

// ========== Тесты стемминга ==========

void test_stemmer_english() {
    Stemmer stemmer;
    
    assert(stemmer.stem("running") == stemmer.stem("runs"));
    assert(stemmer.stem("walking") == stemmer.stem("walked"));
    assert(stemmer.stem("happiness") == stemmer.stem("happy"));
    std::cout << "test_stemmer_english" << std::endl;
}

void test_stemmer_russian() {
    Stemmer stemmer;
    
    // Проверяем, что окончания удаляются
    std::string stem1 = stemmer.stem("кардиология");
    std::string stem2 = stemmer.stem("кардиологии");
    // Основы должны быть похожи (хотя бы первые символы)
    assert(stem1.substr(0, 10) == stem2.substr(0, 10));
    std::cout << " test_stemmer_russian" << std::endl;
}

void test_stemmer_short() {
    Stemmer stemmer;
    
    // Короткие слова не должны обрабатываться
    assert(stemmer.stem("a") == "a");
    assert(stemmer.stem("is") == "is");
    std::cout << " test_stemmer_short" << std::endl;
}

// ========== Тесты HashMap ==========

void test_hashmap_insert_find() {
    HashMap<int> map;
    
    map.insert("key1", 100);
    map.insert("key2", 200);
    map.insert("key3", 300);
    
    int value;
    assert(map.find("key1", value) && value == 100);
    assert(map.find("key2", value) && value == 200);
    assert(map.find("key3", value) && value == 300);
    assert(!map.find("key4", value));
    std::cout << "test_hashmap_insert_find" << std::endl;
}

void test_hashmap_update() {
    HashMap<int> map;
    
    map.insert("key", 100);
    assert(map.size() == 1);
    
    map.insert("key", 200);  // Обновление
    assert(map.size() == 1);  // Размер не изменился
    
    int value;
    map.find("key", value);
    assert(value == 200);
    std::cout << " test_hashmap_update" << std::endl;
}

void test_hashmap_operator() {
    HashMap<std::string> map;
    
    map["hello"] = "world";
    map["foo"] = "bar";
    
    assert(map["hello"] == "world");
    assert(map["foo"] == "bar");
    std::cout << " test_hashmap_operator" << std::endl;
}

void test_hashmap_many() {
    HashMap<int> map;
    
    // Вставить много элементов (проверка rehash)
    for (int i = 0; i < 10000; i++) {
        map.insert("key_" + std::to_string(i), i);
    }
    
    assert(map.size() == 10000);
    
    int value;
    assert(map.find("key_0", value) && value == 0);
    assert(map.find("key_9999", value) && value == 9999);
    assert(map.find("key_5000", value) && value == 5000);
    std::cout << " test_hashmap_many" << std::endl;
}

// ========== Тесты булевых операций ==========

void test_intersect() {
    std::vector<uint32_t> list1 = {1, 3, 5, 7, 9};
    std::vector<uint32_t> list2 = {3, 5, 11};
    
    auto result = Searcher::intersect(list1, list2);
    
    assert(result.size() == 2);
    assert(result[0] == 3);
    assert(result[1] == 5);
    std::cout << "test_intersect" << std::endl;
}

void test_intersect_empty() {
    std::vector<uint32_t> list1 = {1, 2, 3};
    std::vector<uint32_t> list2 = {4, 5, 6};
    
    auto result = Searcher::intersect(list1, list2);
    
    assert(result.empty());
    std::cout << " test_intersect_empty" << std::endl;
}

void test_union() {
    std::vector<uint32_t> list1 = {1, 3, 5};
    std::vector<uint32_t> list2 = {2, 3, 6};
    
    auto result = Searcher::union_lists(list1, list2);
    
    assert(result.size() == 5);
    assert(result[0] == 1);
    assert(result[1] == 2);
    assert(result[2] == 3);
    assert(result[3] == 5);
    assert(result[4] == 6);
    std::cout << " test_union" << std::endl;
}

void test_union_empty() {
    std::vector<uint32_t> list1 = {};
    std::vector<uint32_t> list2 = {1, 2, 3};
    
    auto result = Searcher::union_lists(list1, list2);
    
    assert(result.size() == 3);
    std::cout << " test_union_empty" << std::endl;
}

// ========== Тесты парсера запросов ==========

void test_query_parser_simple() {
    QueryParser parser;
    
    QueryNode* node = parser.parse("hello");
    assert(node != nullptr);
    assert(node->type == NodeType::TERM);
    assert(node->term == "hello");
    delete node;
    std::cout << "test_query_parser_simple" << std::endl;
}

void test_query_parser_and() {
    QueryParser parser;
    
    QueryNode* node = parser.parse("hello && world");
    assert(node != nullptr);
    assert(node->type == NodeType::AND);
    assert(node->left->type == NodeType::TERM);
    assert(node->left->term == "hello");
    assert(node->right->type == NodeType::TERM);
    assert(node->right->term == "world");
    delete node;
    std::cout << " test_query_parser_and" << std::endl;
}

void test_query_parser_or() {
    QueryParser parser;
    
    QueryNode* node = parser.parse("hello || world");
    assert(node != nullptr);
    assert(node->type == NodeType::OR);
    delete node;
    std::cout << " test_query_parser_or" << std::endl;
}

void test_query_parser_not() {
    QueryParser parser;
    
    QueryNode* node = parser.parse("!hello");
    assert(node != nullptr);
    assert(node->type == NodeType::NOT);
    assert(node->left->type == NodeType::TERM);
    assert(node->left->term == "hello");
    delete node;
    std::cout << " test_query_parser_not" << std::endl;
}

void test_query_parser_complex() {
    QueryParser parser;
    
    QueryNode* node = parser.parse("(a || b) && c");
    assert(node != nullptr);
    assert(node->type == NodeType::AND);
    assert(node->left->type == NodeType::OR);
    assert(node->right->type == NodeType::TERM);
    delete node;
    std::cout << " test_query_parser_complex" << std::endl;
}

void test_query_parser_implicit_and() {
    QueryParser parser;
    
    // Пробел = неявное AND
    QueryNode* node = parser.parse("hello world");
    assert(node != nullptr);
    assert(node->type == NodeType::AND);
    delete node;
    std::cout << " test_query_parser_implicit_and" << std::endl;
}

// ========== Главная функция ==========

int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "      UNIT ТЕСТЫ" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << std::endl;
    
    std::cout << "--- Тесты токенизатора ---" << std::endl;
    test_tokenizer_simple();
    test_tokenizer_punctuation();
    test_tokenizer_russian();
    test_tokenizer_mixed();
    test_tokenizer_empty();
    
    std::cout << std::endl << "--- Тесты стемминга ---" << std::endl;
    test_stemmer_english();
    test_stemmer_russian();
    test_stemmer_short();
    
    std::cout << std::endl << "--- Тесты HashMap ---" << std::endl;
    test_hashmap_insert_find();
    test_hashmap_update();
    test_hashmap_operator();
    test_hashmap_many();
    
    std::cout << std::endl << "--- Тесты булевых операций ---" << std::endl;
    test_intersect();
    test_intersect_empty();
    test_union();
    test_union_empty();
    
    std::cout << std::endl << "--- Тесты парсера запросов ---" << std::endl;
    test_query_parser_simple();
    test_query_parser_and();
    test_query_parser_or();
    test_query_parser_not();
    test_query_parser_complex();
    test_query_parser_implicit_and();
    
    std::cout << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "      ВСЕ ТЕСТЫ ПРОЙДЕНЫ!" << std::endl;
    std::cout << "========================================" << std::endl;
    
    return 0;
}

