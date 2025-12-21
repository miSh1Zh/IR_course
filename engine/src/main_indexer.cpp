#include <iostream>
#include <string>
#include <cstring>
#include <chrono>
#include "indexer.hpp"

void print_usage(const char* program) {
    std::cout << "Использование: " << program << " [опции]" << std::endl;
    std::cout << std::endl;
    std::cout << "Опции:" << std::endl;
    std::cout << "  --input=FILE     Входной JSON файл (corpus.json)" << std::endl;
    std::cout << "  --output=FILE    Выходной файл индекса (index.bin)" << std::endl;
    std::cout << "  --stats          Вывести статистику термов" << std::endl;
    std::cout << "  --help           Показать эту справку" << std::endl;
    std::cout << std::endl;
    std::cout << "Пример:" << std::endl;
    std::cout << "  " << program << " --input=../data/corpus.json --output=../data/index.bin" << std::endl;
}

int main(int argc, char* argv[]) {
    std::string input_file;
    std::string output_file;
    bool show_stats = false;
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        } else if (arg.find("--input=") == 0) {
            input_file = arg.substr(8);
        } else if (arg.find("--output=") == 0) {
            output_file = arg.substr(9);
        } else if (arg == "--stats") {
            show_stats = true;
        } else {
            std::cerr << "Неизвестная опция: " << arg << std::endl;
            print_usage(argv[0]);
            return 1;
        }
    }
    
    if (input_file.empty()) {
        input_file = "../data/corpus.json";
        std::cout << "Используется входной файл по умолчанию: " << input_file << std::endl;
    }
    
    if (output_file.empty()) {
        output_file = "../data/index.bin";
        std::cout << "Используется выходной файл по умолчанию: " << output_file << std::endl;
    }
    
    Indexer indexer;
    
    auto start = std::chrono::high_resolution_clock::now();
    indexer.build_from_json(input_file);
    auto build_end = std::chrono::high_resolution_clock::now();
    auto build_duration = std::chrono::duration_cast<std::chrono::milliseconds>(build_end - start);
    
    std::cout << std::endl;
    std::cout << "Время построения: " << build_duration.count() << " мс" << std::endl;
    
    if (show_stats) {
        std::cout << std::endl;
        std::cout << "Топ-20 частых термов:" << std::endl;
        auto term_freqs = indexer.get_term_frequencies();
        
        for (size_t i = 0; i < std::min(term_freqs.size(), size_t(20)); i++) {
            std::cout << "  " << (i + 1) << ". " << term_freqs[i].first 
                      << " - " << term_freqs[i].second << " документов" << std::endl;
        }
    }
    
    indexer.save_to_file(output_file);
    
    auto save_end = std::chrono::high_resolution_clock::now();
    auto save_duration = std::chrono::duration_cast<std::chrono::milliseconds>(save_end - build_end);
    
    std::cout << "Время сохранения: " << save_duration.count() << " мс" << std::endl;
    
    auto total_duration = std::chrono::duration_cast<std::chrono::milliseconds>(save_end - start);
    std::cout << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Общее время: " << total_duration.count() << " мс" << std::endl;
    std::cout << "Документов: " << indexer.get_doc_count() << std::endl;
    std::cout << "Термов: " << indexer.get_term_count() << std::endl;
    std::cout << "Скорость: " << (indexer.get_doc_count() * 1000.0 / total_duration.count()) 
              << " документов/сек" << std::endl;
    std::cout << "========================================" << std::endl;
    
    return 0;
}

