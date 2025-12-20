CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2

# Исходники
SRCS = src/tokenizer.cpp src/stemmer.cpp src/hashmap.cpp src/indexer.cpp src/searcher.cpp src/query_parser.cpp
OBJS = $(SRCS:.cpp=.o)

# Цели
all: indexer searcher

indexer: src/main_indexer.cpp src/tokenizer.cpp src/stemmer.cpp src/hashmap.cpp src/indexer.cpp
	$(CXX) $(CXXFLAGS) -o indexer $^

searcher: src/main_searcher.cpp src/tokenizer.cpp src/stemmer.cpp src/hashmap.cpp src/indexer.cpp src/searcher.cpp src/query_parser.cpp
	$(CXX) $(CXXFLAGS) -o searcher $^

# Тесты
test: test_runner
	./test_runner

test_runner: tests/test_all.cpp src/tokenizer.cpp src/stemmer.cpp src/hashmap.cpp src/indexer.cpp src/searcher.cpp src/query_parser.cpp
	$(CXX) $(CXXFLAGS) -o test_runner $^

# Отдельные тесты
test_tokenizer: tests/test_tokenizer.cpp src/tokenizer.cpp
	$(CXX) $(CXXFLAGS) -o test_tokenizer $^
	./test_tokenizer

test_stemmer: tests/test_stemmer.cpp src/stemmer.cpp
	$(CXX) $(CXXFLAGS) -o test_stemmer $^
	./test_stemmer

test_indexer: tests/test_indexer.cpp src/tokenizer.cpp src/stemmer.cpp src/hashmap.cpp src/indexer.cpp
	$(CXX) $(CXXFLAGS) -o test_indexer $^
	./test_indexer

# Очистка
clean:
	rm -f indexer searcher test_runner test_tokenizer test_stemmer test_indexer
	rm -f src/*.o tests/*.o
	rm -f data/*.bin

# Помощь
help:
	@echo "Доступные цели:"
	@echo "  all        - собрать indexer и searcher"
	@echo "  indexer    - собрать индексатор"
	@echo "  searcher   - собрать поисковик"
	@echo "  test       - запустить все тесты"
	@echo "  clean      - удалить бинарники"

.PHONY: all test clean help

