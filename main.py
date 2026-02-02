#main.py

import sys
from dataclasses import dataclass
import argparse
from typing import List, Tuple

from text_utils import clear_text, sep_words, count_words


@dataclass
class DocumentStats:
    path: str   #путь к файлу
    word_count: int #число слов в тексте
    top_words: List[Tuple[str, int]] #топ слов

def analyze_file(path: str) -> DocumentStats:
    """Анализ файла
    path - путь к файлу
    DocumentStats - итоги анализа"""
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()
    dict = count_words(sep_words(clear_text(text)))
    sorted_dict = {}
    for key in sorted(dict, key=dict.get, reverse=True):
        sorted_dict[key] = dict[key]
    return DocumentStats(path = path, word_count = len(dict), top_words = list(sorted_dict.items())[:10])

def main():
    if len(sys.argv) < 2:
        print("Требуется указать файл")
        sys.exit(1)  # Выход с ошибкой

    parser = argparse.ArgumentParser(
        description="Анализатор текстовых файлов",
        epilog="Пример использования: python main.py input.txt"
    )

    # Обязательный аргумент
    parser.add_argument(
        "input_file",
        help="Путь к файлу для анализа"
    )

    args = parser.parse_args()

    try:
        result = analyze_file(args.input_file)
        print(f"-" * 30)
        print('Анализ файла')
        print(f"-" * 30)
        print(f"Число слов: {result.word_count}")
        print(f"-" * 30)
        print("топ-10 слов: \n")
        for i, (word, count) in enumerate(result.top_words, 1):  # 1 - начинаем с 1
            print(f"{i:2}. Слово '{word}' встречается\t {count:4} раз(а)")
        print(f"-" * 30)
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

main()