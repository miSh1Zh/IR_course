#ifndef INDEXER_HPP
#define INDEXER_HPP

#include <string>
#include <vector>
#include <cstdint>
#include <fstream>
#include "hashmap.hpp"
#include "tokenizer.hpp"
#include "stemmer.hpp"

/**
 * Структура документа в прямом индексе
 */
struct Document {
    uint32_t id;
    std::string title;
    std::string url;
    std::string category;
    std::string source;
};

/**
 * Класс для построения и работы с инвертированным индексом
 */
class Indexer {
public:
    Indexer();
    ~Indexer();
    
    /**
     * Построить индекс из JSON файла (экспорт MongoDB)
     * @param json_file - путь к файлу corpus.json
     */
    void build_from_json(const std::string& json_file);
    
    /**
     * Сохранить индекс в бинарный файл
     * @param index_file - путь к файлу index.bin
     */
    void save_to_file(const std::string& index_file);
    
    /**
     * Загрузить индекс из бинарного файла
     * @param index_file - путь к файлу index.bin
     */
    void load_from_file(const std::string& index_file);
    
    /**
     * Поиск документов по термину
     * @param term - термин для поиска (будет обработан токенизатором и стеммером)
     * @return отсортированный список ID документов
     */
    std::vector<uint32_t> search_term(const std::string& term);
    
    /**
     * Получить документ по ID
     * @param doc_id - ID документа
     * @return структура документа
     */
    Document get_document(uint32_t doc_id) const;
    
    /**
     * Получить количество документов
     */
    uint32_t get_doc_count() const { return static_cast<uint32_t>(forward_index.size()); }
    
    /**
     * Получить количество уникальных термов
     */
    uint32_t get_term_count() const { return term_count; }
    
    /**
     * Получить все термы с их частотами (для анализа Ципфа)
     */
    std::vector<std::pair<std::string, uint32_t>> get_term_frequencies() const;
    
private:
    HashMap<std::vector<uint32_t>> inverted_index;  // term -> [doc_ids]
    std::vector<Document> forward_index;            // doc_id -> document
    
    Tokenizer tokenizer;
    Stemmer stemmer;
    
    uint32_t term_count;
    
    /**
     * Добавить документ в индекс
     */
    void add_document(uint32_t doc_id, const std::string& title, 
                      const std::string& text, const std::string& url,
                      const std::string& category, const std::string& source);
    
    /**
     * Простой парсер JSON (без внешних библиотек)
     */
    std::string extract_json_value(const std::string& json, const std::string& key);
    
    // Магическое число для проверки формата файла
    static constexpr uint32_t MAGIC = 0x5849444D;  // "MIDX"
    static constexpr uint32_t VERSION = 1;
};

#endif // INDEXER_HPP

