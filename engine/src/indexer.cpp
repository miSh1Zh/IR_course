#include "indexer.hpp"
#include <iostream>
#include <algorithm>
#include <cstring>

Indexer::Indexer() : term_count(0) {}

Indexer::~Indexer() {}

std::string Indexer::extract_json_value(const std::string& json, const std::string& key) {
    std::string search_key = "\"" + key + "\"";
    size_t key_pos = json.find(search_key);
    if (key_pos == std::string::npos) return "";
    
    // Найти двоеточие после ключа
    size_t colon_pos = json.find(':', key_pos + search_key.size());
    if (colon_pos == std::string::npos) return "";
    
    // Пропустить пробелы
    size_t value_start = colon_pos + 1;
    while (value_start < json.size() && (json[value_start] == ' ' || json[value_start] == '\t')) {
        value_start++;
    }
    
    if (value_start >= json.size()) return "";
    
    // Проверить тип значения
    if (json[value_start] == '"') {
        // Строковое значение
        size_t str_start = value_start + 1;
        size_t str_end = str_start;
        
        // Найти закрывающую кавычку (с учётом escape)
        while (str_end < json.size()) {
            if (json[str_end] == '"' && (str_end == 0 || json[str_end - 1] != '\\')) {
                break;
            }
            str_end++;
        }
        
        std::string value = json.substr(str_start, str_end - str_start);
        
        // Обработать escape-последовательности
        std::string result;
        for (size_t i = 0; i < value.size(); i++) {
            if (value[i] == '\\' && i + 1 < value.size()) {
                char next = value[i + 1];
                if (next == 'n') { result += '\n'; i++; }
                else if (next == 't') { result += '\t'; i++; }
                else if (next == '"') { result += '"'; i++; }
                else if (next == '\\') { result += '\\'; i++; }
                else { result += value[i]; }
            } else {
                result += value[i];
            }
        }
        
        return result;
    } else if (json[value_start] == 'n') {
        // null
        return "";
    } else {
        // Число или другое
        size_t value_end = value_start;
        while (value_end < json.size() && json[value_end] != ',' && 
               json[value_end] != '}' && json[value_end] != '\n') {
            value_end++;
        }
        return json.substr(value_start, value_end - value_start);
    }
}

void Indexer::add_document(uint32_t doc_id, const std::string& title,
                           const std::string& text, const std::string& url,
                           const std::string& category, const std::string& source) {
    Document doc;
    doc.id = doc_id;
    doc.title = title;
    doc.url = url;
    doc.category = category;
    doc.source = source;
    forward_index.push_back(doc);
    
    std::string full_text = title + " " + text;
    std::vector<std::string> tokens = tokenizer.tokenize(full_text);
    
    HashMap<bool> added_terms;
    
    for (const auto& token : tokens) {
        std::string term = stemmer.stem(token);
        
        if (term.empty()) continue;
        
        bool already_added = false;
        added_terms.find(term, already_added);
        
        if (!already_added) {
            added_terms.insert(term, true);
            inverted_index[term].push_back(doc_id);
        }
    }
}

void Indexer::build_from_json(const std::string& json_file) {
    std::ifstream file(json_file);
    if (!file.is_open()) {
        std::cerr << "Ошибка: не удалось открыть файл " << json_file << std::endl;
        return;
    }
    
    std::cout << "Индексация файла: " << json_file << std::endl;
    
    std::string line;
    uint32_t doc_id = 0;
    uint32_t progress = 0;
    
    while (std::getline(file, line)) {
        if (line.empty() || line[0] != '{') continue;
        
        std::string title = extract_json_value(line, "title");
        std::string text = extract_json_value(line, "text");
        std::string url = extract_json_value(line, "url");
        std::string category = extract_json_value(line, "category");
        std::string source = extract_json_value(line, "source");
        
        if (title.empty() && text.empty()) continue;
        
        add_document(doc_id, title, text, url, category, source);
        doc_id++;
        
        progress++;
        if (progress % 1000 == 0) {
            std::cout << "\rОбработано документов: " << progress << std::flush;
        }
    }
    
    std::cout << "\rОбработано документов: " << doc_id << std::endl;
    
    std::cout << "Сортировка posting lists..." << std::endl;
    auto all_terms = inverted_index.get_all();
    term_count = static_cast<uint32_t>(all_terms.size());
    
    for (const auto& kv : all_terms) {
        std::vector<uint32_t>& postings = inverted_index[kv.key];
        std::sort(postings.begin(), postings.end());
    }
    
    std::cout << "Индексация завершена:" << std::endl;
    std::cout << "  Документов: " << doc_id << std::endl;
    std::cout << "  Термов: " << term_count << std::endl;
    
    file.close();
}

void Indexer::save_to_file(const std::string& index_file) {
    std::ofstream file(index_file, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Ошибка: не удалось создать файл " << index_file << std::endl;
        return;
    }
    
    std::cout << "Сохранение индекса в " << index_file << std::endl;
    
    uint32_t magic = MAGIC;
    uint32_t version = VERSION;
    uint32_t num_terms = term_count;
    uint32_t num_docs = static_cast<uint32_t>(forward_index.size());
    uint64_t forward_offset = 0;
    uint64_t reserved = 0;
    
    file.write(reinterpret_cast<const char*>(&magic), sizeof(magic));
    file.write(reinterpret_cast<const char*>(&version), sizeof(version));
    file.write(reinterpret_cast<const char*>(&num_terms), sizeof(num_terms));
    file.write(reinterpret_cast<const char*>(&num_docs), sizeof(num_docs));
    
    std::streampos forward_offset_pos = file.tellp();
    file.write(reinterpret_cast<const char*>(&forward_offset), sizeof(forward_offset));
    file.write(reinterpret_cast<const char*>(&reserved), sizeof(reserved));
    
    auto all_terms = inverted_index.get_all();
    
    std::sort(all_terms.begin(), all_terms.end(), 
              [](const auto& a, const auto& b) { return a.key < b.key; });
    
    for (const auto& kv : all_terms) {
        uint32_t term_len = static_cast<uint32_t>(kv.key.size());
        file.write(reinterpret_cast<const char*>(&term_len), sizeof(term_len));
        file.write(kv.key.c_str(), term_len);
        
        uint32_t posting_len = static_cast<uint32_t>(kv.value.size());
        file.write(reinterpret_cast<const char*>(&posting_len), sizeof(posting_len));
        file.write(reinterpret_cast<const char*>(kv.value.data()), 
                   posting_len * sizeof(uint32_t));
    }
    
    forward_offset = static_cast<uint64_t>(file.tellp());
    for (const auto& doc : forward_index) {
        // ID
        file.write(reinterpret_cast<const char*>(&doc.id), sizeof(doc.id));
        
        // Title
        uint32_t title_len = static_cast<uint32_t>(doc.title.size());
        file.write(reinterpret_cast<const char*>(&title_len), sizeof(title_len));
        file.write(doc.title.c_str(), title_len);
        
        // URL
        uint32_t url_len = static_cast<uint32_t>(doc.url.size());
        file.write(reinterpret_cast<const char*>(&url_len), sizeof(url_len));
        file.write(doc.url.c_str(), url_len);
        
        // Category
        uint32_t cat_len = static_cast<uint32_t>(doc.category.size());
        file.write(reinterpret_cast<const char*>(&cat_len), sizeof(cat_len));
        file.write(doc.category.c_str(), cat_len);
        
        // Source
        uint32_t src_len = static_cast<uint32_t>(doc.source.size());
        file.write(reinterpret_cast<const char*>(&src_len), sizeof(src_len));
        file.write(doc.source.c_str(), src_len);
    }
    
    file.seekp(forward_offset_pos);
    file.write(reinterpret_cast<const char*>(&forward_offset), sizeof(forward_offset));
    
    file.close();
    
    std::cout << "Индекс сохранён (" << forward_offset << " байт)" << std::endl;
}

void Indexer::load_from_file(const std::string& index_file) {
    std::ifstream file(index_file, std::ios::binary);
    if (!file.is_open()) {
        std::cerr << "Ошибка: не удалось открыть файл " << index_file << std::endl;
        return;
    }
    
    // Читаем заголовок
    uint32_t magic, version, num_terms, num_docs;
    uint64_t forward_offset, reserved;
    
    file.read(reinterpret_cast<char*>(&magic), sizeof(magic));
    file.read(reinterpret_cast<char*>(&version), sizeof(version));
    file.read(reinterpret_cast<char*>(&num_terms), sizeof(num_terms));
    file.read(reinterpret_cast<char*>(&num_docs), sizeof(num_docs));
    file.read(reinterpret_cast<char*>(&forward_offset), sizeof(forward_offset));
    file.read(reinterpret_cast<char*>(&reserved), sizeof(reserved));
    
    if (magic != MAGIC) {
        std::cerr << "Ошибка: неверный формат файла индекса" << std::endl;
        return;
    }
    
    if (version != VERSION) {
        std::cerr << "Ошибка: неподдерживаемая версия индекса" << std::endl;
        return;
    }
    
    term_count = num_terms;
    
    // Читаем инвертированный индекс
    inverted_index.clear();
    
    for (uint32_t i = 0; i < num_terms; i++) {
        // Длина терма
        uint32_t term_len;
        file.read(reinterpret_cast<char*>(&term_len), sizeof(term_len));
        
        // Терм
        std::string term(term_len, '\0');
        file.read(&term[0], term_len);
        
        // Длина posting list
        uint32_t posting_len;
        file.read(reinterpret_cast<char*>(&posting_len), sizeof(posting_len));
        
        // Posting list
        std::vector<uint32_t> postings(posting_len);
        file.read(reinterpret_cast<char*>(postings.data()), posting_len * sizeof(uint32_t));
        
        inverted_index.insert(term, postings);
    }
    
    // Читаем прямой индекс
    forward_index.clear();
    forward_index.reserve(num_docs);
    
    for (uint32_t i = 0; i < num_docs; i++) {
        Document doc;
        
        // ID
        file.read(reinterpret_cast<char*>(&doc.id), sizeof(doc.id));
        
        // Title
        uint32_t title_len;
        file.read(reinterpret_cast<char*>(&title_len), sizeof(title_len));
        doc.title.resize(title_len);
        file.read(&doc.title[0], title_len);
        
        // URL
        uint32_t url_len;
        file.read(reinterpret_cast<char*>(&url_len), sizeof(url_len));
        doc.url.resize(url_len);
        file.read(&doc.url[0], url_len);
        
        // Category
        uint32_t cat_len;
        file.read(reinterpret_cast<char*>(&cat_len), sizeof(cat_len));
        doc.category.resize(cat_len);
        file.read(&doc.category[0], cat_len);
        
        // Source
        uint32_t src_len;
        file.read(reinterpret_cast<char*>(&src_len), sizeof(src_len));
        doc.source.resize(src_len);
        file.read(&doc.source[0], src_len);
        
        forward_index.push_back(doc);
    }
    
    file.close();
    
    std::cout << "Индекс загружен: " << num_docs << " документов, " 
              << num_terms << " термов" << std::endl;
}

std::vector<uint32_t> Indexer::search_term(const std::string& term) {
    // Токенизировать и стеммировать
    std::vector<std::string> tokens = tokenizer.tokenize(term);
    if (tokens.empty()) return {};
    
    std::string stemmed = stemmer.stem(tokens[0]);
    
    std::vector<uint32_t> result;
    inverted_index.find(stemmed, result);
    
    return result;
}

Document Indexer::get_document(uint32_t doc_id) const {
    if (doc_id < forward_index.size()) {
        return forward_index[doc_id];
    }
    return Document{};
}

std::vector<std::pair<std::string, uint32_t>> Indexer::get_term_frequencies() const {
    std::vector<std::pair<std::string, uint32_t>> result;
    
    auto all_terms = inverted_index.get_all();
    for (const auto& kv : all_terms) {
        result.push_back({kv.key, static_cast<uint32_t>(kv.value.size())});
    }
    
    // Сортировать по частоте (убывание)
    std::sort(result.begin(), result.end(),
              [](const auto& a, const auto& b) { return a.second > b.second; });
    
    return result;
}

