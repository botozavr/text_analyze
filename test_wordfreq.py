"""
Тесты для проекта анализа частоты слов.
"""

import pytest
import sys
import os
from io import StringIO
from unittest.mock import patch, mock_open
from typing import List, Dict

from text_utils import clear_text, sep_words, count_words
from wordfreq import analyze_file, DocumentStats, main


class TestTextUtils:
    """Тесты для модуля text_utils.py"""

    def test_clear_text(self):
        """Тест очистки текста от знаков препинания"""
        # Тест 1: Обычный текст со знаками препинания
        text = "Привет, мир! Как дела?"
        result = clear_text(text)
        expected = "Привет мир Как дела"
        assert result == expected, f"Ожидалось: '{expected}', получено: '{result}'"

        # Тест 2: Текст с разными знаками препинания
        text = "Это... тест - с: разными; знаками! препинания?"
        result = clear_text(text)
        expected = "Это тест  с разными знаками препинания"
        assert result == expected

        # Тест 3: Текст без знаков препинания
        text = "Простой текст без знаков препинания"
        result = clear_text(text)
        assert result == text

        # Тест 4: Пустая строка
        assert clear_text("") == ""

    def test_sep_words(self):
        """Тест разделения текста на слова"""
        # Тест 1: Обычный текст
        text = "раз два три"
        result = sep_words(text)
        expected = ["раз", "два", "три"]
        assert result == expected

        # Тест 2: Текст с несколькими пробелами
        text = "раз   два  три"
        result = sep_words(text)
        expected = ["раз", "два", "три"]
        assert result == expected

        # Тест 3: Пустая строка
        assert sep_words("") == []

        # Тест 4: Строка только с пробелами
        assert sep_words("   ") == []

    def test_count_words(self):
        """Тест подсчета частоты слов"""
        # Тест 1: Обычный список слов
        words = ["яблоко", "банан", "яблоко", "апельсин", "банан", "банан"]
        result = count_words(words)
        expected = {"яблоко": 2, "банан": 3, "апельсин": 1}
        assert result == expected

        # Тест 2: Слова в разном регистре (должны считаться разными словами)
        words = ["Слово", "слово", "СЛОВО"]
        result = count_words(words)
        expected = {"Слово": 1, "слово": 1, "СЛОВО": 1}
        assert result == expected

        # Тест 3: Пустой список
        assert count_words([]) == {}

        # Тест 4: Список с одним словом
        assert count_words(["тест"]) == {"тест": 1}

    def test_integration_workflow(self):
        """Интеграционный тест: полный рабочий процесс"""
        text = "Привет, мир! Мир приветствует тебя. Привет ещё раз."

        # Очистка текста
        cleaned = clear_text(text)
        assert cleaned == "Привет мир Мир приветствует тебя Привет ещё раз"

        # Разделение на слова
        words = sep_words(cleaned)
        expected_words = ["Привет", "мир", "Мир", "приветствует", "тебя", "Привет", "ещё", "раз"]
        assert words == expected_words

        # Подсчет частоты
        freq = count_words(words)
        expected_freq = {
            "Привет": 2,
            "мир": 1,
            "Мир": 1,
            "приветствует": 1,
            "тебя": 1,
            "ещё": 1,
            "раз": 1
        }
        assert freq == expected_freq


class TestWordFreq:
    """Тесты для модуля wordfreq.py"""

    def test_document_stats_dataclass(self):
        """Тест dataclass DocumentStats"""
        stats = DocumentStats(
            path="test.txt",
            word_count=5,
            top_words=[("слово", 3), ("тест", 2)]
        )

        assert stats.path == "test.txt"
        assert stats.word_count == 5
        assert stats.top_words == [("слово", 3), ("тест", 2)]

        # Проверка строкового представления
        assert "test.txt" in str(stats)

    @patch("builtins.open", new_callable=mock_open, read_data="Привет, мир! Мир приветствует тебя.")
    def test_analyze_file_success(self, mock_file):
        """Тест успешного анализа файла"""
        result = analyze_file("test.txt", top=3)

        assert isinstance(result, DocumentStats)
        assert result.path == "test.txt"
        assert result.word_count == 5  # уникальных слов: Привет, мир, Мир, приветствует, тебя
        assert len(result.top_words) == 3

        # Проверяем сортировку по частоте
        words = [word for word, count in result.top_words]
        assert "мир" in words or "Мир" in words

    @patch("builtins.open", new_callable=mock_open, read_data="слово слово слово")
    def test_analyze_file_single_word(self, mock_file):
        """Тест анализа файла с одним повторяющимся словом"""
        result = analyze_file("test.txt", top=5)

        assert result.word_count == 1  # одно уникальное слово
        assert result.top_words == [("слово", 3)]

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_analyze_file_empty(self, mock_file):
        """Тест анализа пустого файла"""
        # Перехватываем выход из программы
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            analyze_file("empty.txt")

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    @patch("builtins.open", side_effect=FileNotFoundError("Файл не найден"))
    def test_analyze_file_not_found(self, mock_file):
        """Тест анализа несуществующего файла"""
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            analyze_file("nonexistent.txt")

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def test_analyze_file_top_parameter(self):
        """Тест параметра top в analyze_file"""
        test_data = " ".join(["слово"] * 5 + ["тест"] * 3 + ["пример"] * 2)

        with patch("builtins.open", new_callable=mock_open, read_data=test_data):
            # Тест с top=1
            result1 = analyze_file("test.txt", top=1)
            assert len(result1.top_words) == 1
            assert result1.top_words[0] == ("слово", 5)

            # Тест с top=2
            result2 = analyze_file("test.txt", top=2)
            assert len(result2.top_words) == 2
            assert result2.top_words[0] == ("слово", 5)
            assert result2.top_words[1] == ("тест", 3)


class TestCommandLineInterface:
    """Тесты командного интерфейса"""

    @patch("sys.argv", ["wordfreq.py", "test.txt"])
    @patch("wordfreq.analyze_file")
    def test_main_with_default_top(self, mock_analyze):
        """Тест запуска с параметрами по умолчанию"""
        # Мокаем возвращаемое значение
        mock_analyze.return_value = DocumentStats(
            path="test.txt",
            word_count=10,
            top_words=[("слово", 5), ("тест", 3), ("пример", 2)]
        )

        # Перехватываем вывод
        with patch("sys.stdout", new=StringIO()) as fake_output:
            main()

            output = fake_output.getvalue()
            assert "Анализ файла" in output
            assert "Число слов: 10" in output
            # Проверяем дефолтное значение top=10
            assert "топ-10 слов" in output
            assert "топ-5 слов" not in output  # Убеждаемся, что не выводится top-5

    @patch("sys.argv", ["wordfreq.py", "test.txt", "--top", "5"])
    @patch("wordfreq.analyze_file")
    def test_main_with_custom_top(self, mock_analyze):
        """Тест запуска с кастомным top"""
        mock_analyze.return_value = DocumentStats(
            path="test.txt",
            word_count=3,
            top_words=[("слово", 10), ("тест", 5), ("пример", 3), ("четвертое", 2), ("пятое", 1)]
        )

        with patch("sys.stdout", new=StringIO()) as fake_output:
            main()

            output = fake_output.getvalue()
            # Проверяем, что выводится именно "топ-5"
            assert "топ-5 слов" in output
            # Убеждаемся, что НЕ выводится "топ-10"
            assert "топ-10 слов" not in output

    @patch("sys.argv", ["wordfreq.py", "test.txt", "--top", "3"])
    @patch("wordfreq.analyze_file")
    def test_main_output_format(self, mock_analyze):
        """Тест формата вывода"""
        mock_analyze.return_value = DocumentStats(
            path="test.txt",
            word_count=2,
            top_words=[("первое", 5), ("второе", 3)]
        )

        with patch("sys.stdout", new=StringIO()) as fake_output:
            main()

            output = fake_output.getvalue()

            # Проверяем структуру вывода
            assert "------------------------------" in output
            assert "Анализ файла" in output
            assert "Число слов: 2" in output
            # Проверяем динамический top
            assert "топ-3 слов" in output
            assert "1. Слово 'первое'" in output
            assert "2. Слово 'второе'" in output

    @patch("sys.argv", ["wordfreq.py"])
    def test_main_no_arguments(self):
        """Тест запуска без аргументов"""
        # Перехватываем выход из программы
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main()

        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


class TestEdgeCases:
    """Тесты граничных случаев"""

    def test_special_characters_only(self):
        """Тест текста только со знаками препинания"""
        text = "!!! ??? ... ,,, ---"
        cleaned = clear_text(text)
        assert cleaned == "    "  # Все знаки удалены

        words = sep_words(cleaned)
        assert words == []

        freq = count_words(words)
        assert freq == {}

    def test_numbers_in_text(self):
        """Тест текста с числами"""
        text = "В 2024 году было 100500 случаев"
        cleaned = clear_text(text)
        assert cleaned == "В 2024 году было 100500 случаев"

        words = sep_words(cleaned)
        assert "2024" in words
        assert "100500" in words

    def test_multiline_text(self):
        """Тест многострочного текста"""
        text = """Первая строка.
        Вторая строка!
        Третья строка?"""

        cleaned = clear_text(text)
        words = sep_words(cleaned)

        assert "Первая" in words
        assert "строка" in words
        assert len(words) == 6  # Первая строка Вторая строка Третья строка

    @patch("builtins.open", new_callable=mock_open, read_data="а а а б б в")
    def test_tie_in_frequency(self, mock_file):
        """Тест случая, когда слова имеют одинаковую частоту"""
        result = analyze_file("test.txt", top=10)

        # Проверяем, что слова отсортированы
        counts = [count for word, count in result.top_words]
        assert counts == sorted(counts, reverse=True)


def test_imports():
    """Тест корректности импортов"""
    # Проверяем, что модули импортируются без ошибок
    from text_utils import clear_text, sep_words, count_words
    from wordfreq import analyze_file, DocumentStats, main

    assert callable(clear_text)
    assert callable(sep_words)
    assert callable(count_words)
    assert callable(analyze_file)
    assert callable(main)


if __name__ == "__main__":
    # Запуск тестов напрямую, если нужно
    pytest.main([__file__, "-v"])