#include "query_parser.hpp"
#include <cctype>

QueryNode* QueryParser::parse(const std::string& query) {
    input = query;
    pos = 0;
    
    if (query.empty()) {
        return nullptr;
    }
    
    skip_whitespace();
    
    if (pos >= input.size()) {
        return nullptr;
    }
    
    return parse_or();
}

void QueryParser::skip_whitespace() {
    while (pos < input.size() && (input[pos] == ' ' || input[pos] == '\t')) {
        pos++;
    }
}

char QueryParser::peek() const {
    if (pos >= input.size()) return '\0';
    return input[pos];
}

char QueryParser::get() {
    if (pos >= input.size()) return '\0';
    return input[pos++];
}

QueryNode* QueryParser::parse_or() {
    QueryNode* left = parse_and();
    if (!left) return nullptr;
    
    skip_whitespace();
    
    while (pos + 1 < input.size() && input[pos] == '|' && input[pos + 1] == '|') {
        pos += 2;
        skip_whitespace();
        
        QueryNode* right = parse_and();
        if (!right) {
            delete left;
            return nullptr;
        }
        
        QueryNode* node = new QueryNode();
        node->type = NodeType::OR;
        node->left = left;
        node->right = right;
        left = node;
        
        skip_whitespace();
    }
    
    return left;
}

QueryNode* QueryParser::parse_and() {
    QueryNode* left = parse_not();
    if (!left) return nullptr;
    
    skip_whitespace();
    
    while (true) {
        if (pos + 1 < input.size() && input[pos] == '&' && input[pos + 1] == '&') {
            pos += 2;
            skip_whitespace();
            
            QueryNode* right = parse_not();
            if (!right) {
                delete left;
                return nullptr;
            }
            
            QueryNode* node = new QueryNode();
            node->type = NodeType::AND;
            node->left = left;
            node->right = right;
            left = node;
            
            skip_whitespace();
            continue;
        }
        
        if (pos < input.size()) {
            char c = input[pos];
            
            if (c == '|' || c == ')' || c == '\0') {
                break;
            }
            
            if (std::isalpha(static_cast<unsigned char>(c)) || 
                c == '!' || c == '(' ||
                (static_cast<unsigned char>(c) >= 0xD0)) {
                
                QueryNode* right = parse_not();
                if (!right) {
                    delete left;
                    return nullptr;
                }
                
                QueryNode* node = new QueryNode();
                node->type = NodeType::AND;
                node->left = left;
                node->right = right;
                left = node;
                
                skip_whitespace();
                continue;
            }
        }
        
        break;
    }
    
    return left;
}

QueryNode* QueryParser::parse_not() {
    skip_whitespace();
    
    if (peek() == '!') {
        get();
        skip_whitespace();
        
        QueryNode* operand = parse_not();
        if (!operand) return nullptr;
        
        QueryNode* node = new QueryNode();
        node->type = NodeType::NOT;
        node->left = operand;
        return node;
    }
    
    return parse_primary();
}

QueryNode* QueryParser::parse_primary() {
    skip_whitespace();
    
    if (peek() == '(') {
        get();
        
        QueryNode* expr = parse_or();
        if (!expr) return nullptr;
        
        skip_whitespace();
        
        if (peek() != ')') {
            delete expr;
            return nullptr;
        }
        get();
        
        return expr;
    }
    
    return parse_term();
}

QueryNode* QueryParser::parse_term() {
    skip_whitespace();
    
    std::string term;
    
    while (pos < input.size()) {
        char c = input[pos];
        unsigned char uc = static_cast<unsigned char>(c);
        
        if (std::isalnum(uc)) {
            term += c;
            pos++;
            continue;
        }
        
        if (uc == 0xD0 || uc == 0xD1) {
            if (pos + 1 < input.size()) {
                term += c;
                term += input[pos + 1];
                pos += 2;
                continue;
            }
        }
        
        if (c == '-' && !term.empty() && pos + 1 < input.size()) {
            unsigned char next = static_cast<unsigned char>(input[pos + 1]);
            if (std::isalnum(next) || next == 0xD0 || next == 0xD1) {
                term += c;
                pos++;
                continue;
            }
        }
        
        break;
    }
    
    if (term.empty()) {
        return nullptr;
    }
    
    QueryNode* node = new QueryNode();
    node->type = NodeType::TERM;
    node->term = term;
    
    return node;
}

