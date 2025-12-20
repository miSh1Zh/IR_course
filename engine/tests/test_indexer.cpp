#include <iostream>
#include <cassert>
#include <fstream>
#include "../src/indexer.hpp"

void test_build_and_search() {
    // Создать тестовый JSON
    const char* test_json = 
        "{\"title\": \"Test Article\", \"text\": \"Hello world test\", \"url\": \"http://test/1\", \"source\": \"test\", \"category\": \"Test\"}\n"
        "{\"title\": \"Another Article\", \"text\": \"Another test hello\", \"url\": \"http://test/2\", \"source\": \"test\", \"category\": \"Test\"}\n";
    
    std::ofstream file("test_corpus.json");
    file << test_json;
    file.close();
    
    // Построить индекс
    Indexer indexer;
    indexer.build_from_json("test_corpus.json");
    
    assert(indexer.get_doc_count() == 2);
    std::cout << " build index" << std::endl;
    
    // Поиск
    auto results = indexer.search_term("hello");
    assert(results.size() == 2);  // Оба документа содержат hello
    std::cout << " search term" << std::endl;
    
    results = indexer.search_term("world");
    assert(results.size() == 1);  // Только первый
    std::cout << " search specific term" << std::endl;
    
    // Сохранить и загрузить
    indexer.save_to_file("test_index.bin");
    
    Indexer indexer2;
    indexer2.load_from_file("test_index.bin");
    
    assert(indexer2.get_doc_count() == 2);
    std::cout << " save/load index" << std::endl;
    
    results = indexer2.search_term("hello");
    assert(results.size() == 2);
    std::cout << " search after reload" << std::endl;
    
    // Очистка
    std::remove("test_corpus.json");
    std::remove("test_index.bin");
}

int main() {
    std::cout << "=== Тесты индексатора ===" << std::endl;
    test_build_and_search();
    std::cout << "Все тесты пройдены!" << std::endl;
    return 0;
}

