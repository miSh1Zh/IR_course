#ifndef QUERY_PARSER_HPP
#define QUERY_PARSER_HPP

#include <string>
#include <memory>

/**
 * Тип узла дерева запроса
 */
enum class NodeType {
    TERM,   // Терм (слово)
    AND,    // Логическое И
    OR,     // Логическое ИЛИ
    NOT     // Логическое НЕ
};

/**
 * Узел дерева запроса
 */
struct QueryNode {
    NodeType type;
    std::string term;       // Для TERM
    QueryNode* left;        // Левый операнд
    QueryNode* right;       // Правый операнд (для бинарных операторов)
    
    QueryNode() : type(NodeType::TERM), left(nullptr), right(nullptr) {}
    ~QueryNode() {
        delete left;
        delete right;
    }
};

/**
 * Парсер булевых запросов
 * 
 * Синтаксис:
 *   - Пробел или && - логическое И
 *   - || - логическое ИЛИ
 *   - ! - логическое НЕ
 *   - Скобки для группировки
 * 
 * Примеры:
 *   - "московский авиационный институт"
 *   - "красный || желтый"
 *   - "диабет && лечение"
 *   - "!хирургия"
 *   - "(красный || желтый) && автомобиль"
 */
class QueryParser {
public:
    /**
     * Распарсить строку запроса
     * @param query - строка запроса
     * @return корень дерева запроса (nullptr если ошибка)
     */
    QueryNode* parse(const std::string& query);
    
private:
    std::string input;
    size_t pos;
    
    // Пропустить пробелы
    void skip_whitespace();
    
    // Проверить текущий символ
    char peek() const;
    
    // Получить текущий символ и перейти к следующему
    char get();
    
    // Рекурсивный спуск
    QueryNode* parse_or();      // Низший приоритет
    QueryNode* parse_and();     // Средний приоритет
    QueryNode* parse_not();     // Высший приоритет (унарный)
    QueryNode* parse_primary(); // Терм или скобки
    QueryNode* parse_term();    // Одно слово
};

#endif // QUERY_PARSER_HPP

