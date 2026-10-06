"""Подтверждение ошибок ИИ-ассистента исполнением."""

import dataclasses

from ai_publication import Publication, same_publication


def check_missing_journal_title():
    """Вопрос 1. Все ли свойства учтены? Нет поля journal_title."""
    fields = {f.name for f in dataclasses.fields(Publication)}
    print("A. Поля Publication:", sorted(fields))
    print("   'journal_title' присутствует:", "journal_title" in fields)


def check_same_publication_only_title():
    """Вопрос 1. Все ли свойства учтены? Сравнение только по title."""

    def fake_same(a, b):  # normalize в str нет, подменяем на lower
        return a.title.lower() == b.title.lower()

    a = Publication("Обзор методов", "A", "2025", doi="10.5555/a")
    b = Publication("Обзор методов", "B", "2025", doi="10.5555/b")
    print(
        "B. fake_same(a, b):",
        fake_same(a, b),
        "— разные DOI, но одна 'публикация'",
    )


def check_year_type():
    """Вопрос 2. Ограничены ли допустимые значения? year: str."""
    p = Publication("T", "A", "двадцать пятый")
    print("C. year =", repr(p.year), "— строка принята")


def check_title_empty():
    """Вопрос 2. Ограничены ли допустимые значения? title без проверки."""
    p1 = Publication("", "A", "2025")
    p2 = Publication("   ", "A", "2025")
    print(
        "D. title =",
        repr(p1.title),
        ",",
        repr(p2.title),
        "— пустое и из пробелов приняты",
    )


def check_doi_empty_string():
    """Вопрос 3. Как обозначено отсутствие значения? doi = ''."""
    p1 = Publication("T", "A", "2025")  # doi по умолчанию ""
    p2 = Publication("T", "A", "2025", doi="")  # явно ""
    print(
        "E. p1.doi == p2.doi:",
        p1.doi == p2.doi,
        "— 'нет DOI' смешано с 'пустой DOI'",
    )


def check_issn_empty_string():
    """Вопрос 3. Как обозначено отсутствие значения? issn = ''."""
    p = Publication("T", "A", "2025")
    print(
        "F. issn =",
        repr(p.issn),
        "— отсутствие ISSN представлено пустой строкой",
    )


def check_authors_multiplicity():
    """Вопрос 4. Учтена ли множественность? authors: str."""
    p = Publication("T", "Иванов, Петров, Сидоров", "2025")
    print("G. authors =", repr(p.authors), "— сколько авторов? Неоднозначно")


def check_issn_multiplicity():
    """Вопрос 4. Учтена ли множественность? issn: str."""
    p = Publication("T", "A", "2025", issn="0040-6090")
    print("H. issn =", repr(p.issn), "— второй ISSN (1879-2731) задать некуда")


def check_normalize_method():
    """Вопрос 5. Существует ли упомянутый метод?"""
    a = Publication("T", "A", "2025")
    b = Publication("T", "B", "2025")
    try:
        same_publication(a, b)
    except AttributeError as e:
        print("I. AttributeError:", e)


if __name__ == "__main__":
    check_missing_journal_title()
    check_same_publication_only_title()
    check_year_type()
    check_title_empty()
    check_doi_empty_string()
    check_issn_empty_string()
    check_authors_multiplicity()
    check_issn_multiplicity()
    check_normalize_method()
