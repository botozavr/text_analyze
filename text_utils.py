"""
1.	Написать модуль text_utils.py с функциями:
o	очистка текста от знаков препинания,
o	разбиение на слова,
o	подсчёт частоты слов (возврат dict).
"""

#text_utils.py

from re import sub
from typing import List, Dict

def clear_text(my_str: str) -> str:
    """Очищает текст от знаков препинания"""
    return sub(r'[^\w\s]', '', my_str)

def sep_words (my_str: str) -> List[str]:
    """"Разделяет текст на слова"""
    return my_str.split()

def count_words(words: List[str]) -> Dict[str, int]:
    """Подсчёт частоты слов"""
    x = {}
    for i in words:
        if i in x:
            x[i]+=1
        else:
            x[i] = 1
    return x


