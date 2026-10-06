"""Нормализация идентификаторов."""

import re

ISSN_PATTERN = re.compile(r"[0-9]{7}[0-9X]")
DOI_PATTERN = re.compile(r"10\.[0-9]{4,9}/\S+")  # шаблон DOI
DOI_PREFIXES = (
    "https://doi.org/",
    "http://doi.org/",
    "https://dx.doi.org/",
    "http://dx.doi.org/",
    "doi:",
)


def normalize_issn(value: str | None) -> str | None:
    """Приводит ISSN к восьми символам или возвращает None."""
    if not value:
        return None
    chars = "".join(c for c in value.upper() if c.isalnum())
    return chars if ISSN_PATTERN.fullmatch(chars) else None


def normalize_doi(value: str | None) -> str | None:
    """Приводит DOI к нижнему регистру без префикса или возвращает None.

    Требования к результату приведены в таблице методических указаний.
    """
    if value is None:
        return None
    cleaned = value.strip().lower()
    if not cleaned:
        return None
    for prefix in DOI_PREFIXES:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
            break
    return cleaned if DOI_PATTERN.fullmatch(cleaned) else None


def issn_check_digit_ok(issn: str) -> bool:
    """Проверяет контрольный разряд нормализованного ISSN.

    Ожидает строку из 8 символов: 7 цифр и контрольный символ
    (цифра или X). Возвращает True, если контроль сходится.
    """
    if len(issn) != 8:
        return False
    if not issn[:7].isdigit():
        return False

    digits = [int(c) for c in issn[:7]]
    weights = [8, 7, 6, 5, 4, 3, 2]
    total = sum(w * d for w, d in zip(weights, digits, strict=True))
    check = (11 - total % 11) % 11
    expected = "X" if check == 10 else str(check)

    return issn[7] == expected
