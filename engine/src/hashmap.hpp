#ifndef HASHMAP_HPP
#define HASHMAP_HPP

#include <string>
#include <vector>
#include <cstdint>

/**
 * Самостоятельная реализация хеш-таблицы (без std::unordered_map)
 * Использует метод цепочек для разрешения коллизий
 * 
 * @tparam V - тип значения
 */
template<typename V>
class HashMap {
public:
    /**
     * Конструктор
     * @param initial_size - начальный размер таблицы
     */
    HashMap(size_t initial_size = 10007);
    
    /**
     * Деструктор - освобождает память
     */
    ~HashMap();
    
    /**
     * Вставить или обновить элемент
     * @param key - ключ (строка)
     * @param value - значение
     */
    void insert(const std::string& key, const V& value);
    
    /**
     * Найти элемент по ключу
     * @param key - ключ
     * @param value - выходное значение (если найдено)
     * @return true если найдено
     */
    bool find(const std::string& key, V& value) const;
    
    /**
     * Получить ссылку на значение (создаёт если не существует)
     * @param key - ключ
     * @return ссылка на значение
     */
    V& operator[](const std::string& key);
    
    /**
     * Проверить наличие ключа
     * @param key - ключ
     * @return true если ключ существует
     */
    bool contains(const std::string& key) const;
    
    /**
     * Получить количество элементов
     */
    size_t size() const { return count; }
    
    /**
     * Проверить, пустая ли таблица
     */
    bool empty() const { return count == 0; }
    
    /**
     * Очистить таблицу
     */
    void clear();
    
    /**
     * Структура для итерации
     */
    struct KeyValue {
        std::string key;
        V value;
    };
    
    /**
     * Получить все пары ключ-значение
     * @return вектор пар
     */
    std::vector<KeyValue> get_all() const;
    
    /**
     * Получить все ключи
     */
    std::vector<std::string> keys() const;
    
private:
    /**
     * Узел цепочки
     */
    struct Node {
        std::string key;
        V value;
        Node* next;
        
        Node(const std::string& k, const V& v) : key(k), value(v), next(nullptr) {}
    };
    
    std::vector<Node*> buckets;  // Массив корзин
    size_t count;                // Количество элементов
    
    /**
     * Хеш-функция (djb2)
     */
    size_t hash(const std::string& key) const;
    
    /**
     * Перехешировать при высокой загрузке
     */
    void rehash();
    
    /**
     * Фактор загрузки для перехеширования
     */
    static constexpr float LOAD_FACTOR = 0.75f;
};

// ============== Реализация шаблона ==============

template<typename V>
HashMap<V>::HashMap(size_t initial_size) : count(0) {
    buckets.resize(initial_size, nullptr);
}

template<typename V>
HashMap<V>::~HashMap() {
    clear();
}

template<typename V>
size_t HashMap<V>::hash(const std::string& key) const {
    // djb2 хеш-функция
    size_t hash = 5381;
    for (char c : key) {
        hash = ((hash << 5) + hash) + static_cast<unsigned char>(c);
    }
    return hash % buckets.size();
}

template<typename V>
void HashMap<V>::insert(const std::string& key, const V& value) {
    // Проверить загрузку
    if (static_cast<float>(count + 1) / buckets.size() > LOAD_FACTOR) {
        rehash();
    }
    
    size_t idx = hash(key);
    Node* node = buckets[idx];
    
    // Поиск существующего ключа
    while (node != nullptr) {
        if (node->key == key) {
            node->value = value;  // Обновить значение
            return;
        }
        node = node->next;
    }
    
    // Добавить новый узел
    Node* new_node = new Node(key, value);
    new_node->next = buckets[idx];
    buckets[idx] = new_node;
    count++;
}

template<typename V>
bool HashMap<V>::find(const std::string& key, V& value) const {
    size_t idx = hash(key);
    Node* node = buckets[idx];
    
    while (node != nullptr) {
        if (node->key == key) {
            value = node->value;
            return true;
        }
        node = node->next;
    }
    
    return false;
}

template<typename V>
V& HashMap<V>::operator[](const std::string& key) {
    // Проверить загрузку
    if (static_cast<float>(count + 1) / buckets.size() > LOAD_FACTOR) {
        rehash();
    }
    
    size_t idx = hash(key);
    Node* node = buckets[idx];
    
    // Поиск существующего ключа
    while (node != nullptr) {
        if (node->key == key) {
            return node->value;
        }
        node = node->next;
    }
    
    // Создать новый узел с пустым значением
    Node* new_node = new Node(key, V());
    new_node->next = buckets[idx];
    buckets[idx] = new_node;
    count++;
    
    return new_node->value;
}

template<typename V>
bool HashMap<V>::contains(const std::string& key) const {
    size_t idx = hash(key);
    Node* node = buckets[idx];
    
    while (node != nullptr) {
        if (node->key == key) {
            return true;
        }
        node = node->next;
    }
    
    return false;
}

template<typename V>
void HashMap<V>::clear() {
    for (size_t i = 0; i < buckets.size(); i++) {
        Node* node = buckets[i];
        while (node != nullptr) {
            Node* next = node->next;
            delete node;
            node = next;
        }
        buckets[i] = nullptr;
    }
    count = 0;
}

template<typename V>
void HashMap<V>::rehash() {
    std::vector<Node*> old_buckets = std::move(buckets);
    
    // Увеличить размер примерно вдвое (следующее простое число)
    size_t new_size = old_buckets.size() * 2 + 1;
    buckets.resize(new_size, nullptr);
    count = 0;
    
    // Перенести все элементы
    for (size_t i = 0; i < old_buckets.size(); i++) {
        Node* node = old_buckets[i];
        while (node != nullptr) {
            Node* next = node->next;
            
            // Добавить в новую таблицу
            size_t idx = hash(node->key);
            node->next = buckets[idx];
            buckets[idx] = node;
            count++;
            
            node = next;
        }
    }
}

template<typename V>
std::vector<typename HashMap<V>::KeyValue> HashMap<V>::get_all() const {
    std::vector<KeyValue> result;
    result.reserve(count);
    
    for (size_t i = 0; i < buckets.size(); i++) {
        Node* node = buckets[i];
        while (node != nullptr) {
            result.push_back({node->key, node->value});
            node = node->next;
        }
    }
    
    return result;
}

template<typename V>
std::vector<std::string> HashMap<V>::keys() const {
    std::vector<std::string> result;
    result.reserve(count);
    
    for (size_t i = 0; i < buckets.size(); i++) {
        Node* node = buckets[i];
        while (node != nullptr) {
            result.push_back(node->key);
            node = node->next;
        }
    }
    
    return result;
}

#endif // HASHMAP_HPP

