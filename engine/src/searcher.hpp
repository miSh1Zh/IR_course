#ifndef SEARCHER_HPP
#define SEARCHER_HPP

#include <vector>
#include <cstdint>
#include "indexer.hpp"
#include "query_parser.hpp"

/**
 * Класс для выполнения булевого поиска
 */
class Searcher {
public:
    /**
     * Конструктор
     * @param idx - указатель на индексатор
     */
    Searcher(Indexer* idx);
    
    /**
     * Выполнить поиск по запросу
     * @param query - строка запроса
     * @return отсортированный список ID документов
     */
    std::vector<uint32_t> search(const std::string& query);
    
    /**
     * Пересечение двух отсортированных списков (AND)
     */
    static std::vector<uint32_t> intersect(const std::vector<uint32_t>& list1,
                                           const std::vector<uint32_t>& list2);
    
    /**
     * Объединение двух отсортированных списков (OR)
     */
    static std::vector<uint32_t> union_lists(const std::vector<uint32_t>& list1,
                                             const std::vector<uint32_t>& list2);
    
    /**
     * Отрицание списка (NOT) - все документы кроме указанных
     */
    std::vector<uint32_t> negate(const std::vector<uint32_t>& list);
    
private:
    Indexer* indexer;
    QueryParser parser;
    
    /**
     * Рекурсивное выполнение запроса по дереву
     */
    std::vector<uint32_t> execute(QueryNode* node);
};

#endif // SEARCHER_HPP

