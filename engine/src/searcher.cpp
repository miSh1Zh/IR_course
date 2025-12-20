#include "searcher.hpp"
#include "tokenizer.hpp"
#include "stemmer.hpp"
#include <algorithm>
#include <iostream>

Searcher::Searcher(Indexer* idx) : indexer(idx) {}

std::vector<uint32_t> Searcher::search(const std::string& query) {
    QueryNode* root = parser.parse(query);
    
    if (!root) {
        Tokenizer tokenizer;
        
        std::vector<std::string> tokens = tokenizer.tokenize(query);
        if (tokens.empty()) return {};
        
        std::vector<uint32_t> result = indexer->search_term(tokens[0]);
        
        for (size_t i = 1; i < tokens.size() && !result.empty(); i++) {
            std::vector<uint32_t> next = indexer->search_term(tokens[i]);
            result = intersect(result, next);
        }
        
        return result;
    }
    
    std::vector<uint32_t> result = execute(root);
    delete root;
    
    return result;
}

std::vector<uint32_t> Searcher::execute(QueryNode* node) {
    if (!node) return {};
    
    switch (node->type) {
        case NodeType::TERM: {
            Tokenizer tokenizer;
            Stemmer stemmer;
            
            std::vector<std::string> tokens = tokenizer.tokenize(node->term);
            if (tokens.empty()) return {};
            
            std::string stemmed = stemmer.stem(tokens[0]);
            return indexer->search_term(stemmed);
        }
        
        case NodeType::AND: {
            std::vector<uint32_t> left = execute(node->left);
            if (left.empty()) return {};
            
            std::vector<uint32_t> right = execute(node->right);
            return intersect(left, right);
        }
        
        case NodeType::OR: {
            std::vector<uint32_t> left = execute(node->left);
            std::vector<uint32_t> right = execute(node->right);
            return union_lists(left, right);
        }
        
        case NodeType::NOT: {
            std::vector<uint32_t> operand = execute(node->left);
            return negate(operand);
        }
    }
    
    return {};
}

std::vector<uint32_t> Searcher::intersect(const std::vector<uint32_t>& list1,
                                          const std::vector<uint32_t>& list2) {
    std::vector<uint32_t> result;
    
    size_t i = 0, j = 0;
    
    while (i < list1.size() && j < list2.size()) {
        if (list1[i] == list2[j]) {
            result.push_back(list1[i]);
            i++;
            j++;
        } else if (list1[i] < list2[j]) {
            i++;
        } else {
            j++;
        }
    }
    
    return result;
}

std::vector<uint32_t> Searcher::union_lists(const std::vector<uint32_t>& list1,
                                            const std::vector<uint32_t>& list2) {
    std::vector<uint32_t> result;
    result.reserve(list1.size() + list2.size());
    
    size_t i = 0, j = 0;
    
    while (i < list1.size() || j < list2.size()) {
        if (i >= list1.size()) {
            result.push_back(list2[j++]);
        } else if (j >= list2.size()) {
            result.push_back(list1[i++]);
        } else if (list1[i] < list2[j]) {
            result.push_back(list1[i++]);
        } else if (list1[i] > list2[j]) {
            result.push_back(list2[j++]);
        } else {
            result.push_back(list1[i]);
            i++;
            j++;
        }
    }
    
    return result;
}

std::vector<uint32_t> Searcher::negate(const std::vector<uint32_t>& list) {
    std::vector<uint32_t> result;
    
    uint32_t total_docs = indexer->get_doc_count();
    size_t list_idx = 0;
    
    for (uint32_t doc_id = 0; doc_id < total_docs; doc_id++) {
        while (list_idx < list.size() && list[list_idx] < doc_id) {
            list_idx++;
        }
        
        if (list_idx >= list.size() || list[list_idx] != doc_id) {
            result.push_back(doc_id);
        }
    }
    
    return result;
}

