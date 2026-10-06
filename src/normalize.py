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
