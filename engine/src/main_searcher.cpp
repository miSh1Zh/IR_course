#include <iostream>
#include <string>
#include <chrono>
#include "indexer.hpp"
#include "searcher.hpp"

void print_usage(const char* program) {
    std::cout << "Использование: " << program << " [опции]" << std::endl;
    std::cout << std::endl;
    std::cout << "Опции:" << std::endl;
    std::cout << "  --index=FILE     Файл индекса (index.bin)" << std::endl;
    std::cout << "  --query=QUERY    Поисковый запрос (однократный режим)" << std::endl;
    std::cout << "  --batch          Пакетный режим: запросы из stdin" << std::endl;
    std::cout << "  --limit=N        Максимальное количество результатов (по умолчанию 50)" << std::endl;
    std::cout << "  --help           Показать эту справку" << std::endl;
    std::cout << std::endl;
    std::cout << "Примеры:" << std::endl;
    std::cout << "  " << program << " --index=data/index.bin --query=\"кардиология\"" << std::endl;
    std::cout << "  " << program << " --index=data/index.bin --query=\"диабет && лечение\"" << std::endl;
    std::cout << "  cat queries.txt | " << program << " --index=data/index.bin --batch" << std::endl;
    std::cout << std::endl;
    std::cout << "Синтаксис запросов:" << std::endl;
    std::cout << "  term1 term2      - AND (неявное)" << std::endl;
    std::cout << "  term1 && term2   - AND (явное)" << std::endl;
    std::cout << "  term1 || term2   - OR" << std::endl;
    std::cout << "  !term            - NOT" << std::endl;
    std::cout << "  (term1 || term2) && term3 - скобки" << std::endl;
}

void print_results(Indexer& indexer, const std::vector<uint32_t>& results, int limit) {
    std::cout << "Найдено: " << results.size() << " документов" << std::endl;
    
    int count = 0;
    for (uint32_t doc_id : results) {
        if (count >= limit) {
            std::cout << "и еще " << (results.size() - limit) << " документов" << std::endl;
            break;
        }
        
        Document doc = indexer.get_document(doc_id);
        std::cout << (count + 1) << ". " << doc.title << std::endl;
        std::cout << "   " << doc.url << std::endl;
        if (!doc.category.empty()) {
            std::cout << "   [" << doc.category << "]" << std::endl;
        }
        std::cout << std::endl;
        
        count++;
    }
}

int main(int argc, char* argv[]) {
    std::string index_file;
    std::string query;
    bool batch_mode = false;
    int limit = 50;
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        } else if (arg.find("--index=") == 0) {
            index_file = arg.substr(8);
        } else if (arg.find("--query=") == 0) {
            query = arg.substr(8);
        } else if (arg == "--batch") {
            batch_mode = true;
        } else if (arg.find("--limit=") == 0) {
            limit = std::stoi(arg.substr(8));
        } else {
            std::cerr << "Неизвестная опция: " << arg << std::endl;
            print_usage(argv[0]);
            return 1;
        }
    }
    
    if (index_file.empty()) {
        index_file = "data/index.bin";
    }
    
    Indexer indexer;
    indexer.load_from_file(index_file);
    
    if (indexer.get_doc_count() == 0) {
        std::cerr << "Ошибка: индекс пуст или не загружен" << std::endl;
        return 1;
    }
    
    Searcher searcher(&indexer);
    
    if (!query.empty()) {
        std::cout << "Запрос: " << query << std::endl;
        std::cout << "----------------------------------------" << std::endl;
        
        auto start = std::chrono::high_resolution_clock::now();
        std::vector<uint32_t> results = searcher.search(query);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        
        print_results(indexer, results, limit);
        
        std::cout << "Время поиска: " << duration.count() << " мкс" << std::endl;
        
    } else if (batch_mode) {
        std::string line;
        while (std::getline(std::cin, line)) {
            if (line.empty()) continue;
            
            std::cout << "Q: " << line << std::endl;
            
            auto start = std::chrono::high_resolution_clock::now();
            std::vector<uint32_t> results = searcher.search(line);
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            std::cout << "R: " << results.size() << " документов (" 
                      << duration.count() << " мкс)" << std::endl;
            
            int count = 0;
            for (uint32_t doc_id : results) {
                if (count >= limit) break;
                Document doc = indexer.get_document(doc_id);
                std::cout << "   - " << doc.title << std::endl;
                count++;
            }
            
            std::cout << "---" << std::endl;
        }
        
    } else {
        std::cout << "========================================" << std::endl;
        std::cout << "      ПОИСКОВАЯ СИСТЕМА" << std::endl;
        std::cout << "========================================" << std::endl;
        std::cout << "Документов в индексе: " << indexer.get_doc_count() << std::endl;
        std::cout << "Термов: " << indexer.get_term_count() << std::endl;
        std::cout << std::endl;
        std::cout << "Введите запрос (или 'quit' для выхода):" << std::endl;
        
        std::string line;
        while (true) {
            std::cout << "> ";
            if (!std::getline(std::cin, line)) break;
            
            if (line == "quit" || line == "exit" || line == "q") {
                break;
            }
            
            if (line.empty()) continue;
            
            auto start = std::chrono::high_resolution_clock::now();
            std::vector<uint32_t> results = searcher.search(line);
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
            
            print_results(indexer, results, limit);
            std::cout << "Время: " << duration.count() << " мкс" << std::endl;
            std::cout << std::endl;
        }
    }
    
    return 0;
}

