// HashMap реализация находится в hashmap.hpp (шаблонный класс)
// Этот файл нужен только для компиляции

#include "hashmap.hpp"

// Явное инстанцирование для используемых типов
template class HashMap<std::vector<uint32_t>>;
template class HashMap<uint32_t>;
template class HashMap<std::string>;

