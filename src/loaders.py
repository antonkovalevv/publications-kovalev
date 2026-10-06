"""Чтение выгрузок и входной контроль данных."""

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from src.models import Publication
from src.normalize import normalize_doi, normalize_issn


class CrossrefDate(BaseModel):
    """Дата выхода публикации в формате Crossref."""

    date_parts: list[list[int | None]] = Field(alias="date-parts")


class CrossrefAuthor(BaseModel):
    """Автор в формате Crossref."""

    family: str | None = None
    given: str | None = None


class CrossrefWork(BaseModel):
    doi: str = Field(alias="DOI")
    title: list[str] = Field(min_length=1)
    issn: list[str] = Field(default_factory=list, alias="ISSN")
    journal: list[str] = Field(default_factory=list, alias="container-title")
    author: list[CrossrefAuthor] = Field(default_factory=list)
    issued: CrossrefDate | None = None


class OpenAlexSource(BaseModel):
    """Источник (издание) в записи OpenAlex."""

    display_name: str | None = None
    issn_l: str | None = None
    issn: list[str] | None = None


class OpenAlexLocation(BaseModel):
    """Локация публикации в записи OpenAlex."""

    source: OpenAlexSource | None = None


class OpenAlexWork(BaseModel):
    """Запись OpenAlex о публикации."""

    doi: str | None = None
    title: str | None = None
    publication_year: int | None = None
    primary_location: OpenAlexLocation | None = None


def load_items(path: Path) -> list[dict[str, Any]]:
    """Читает файл ответа Crossref и возвращает список записей."""
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    items: list[dict[str, Any]] = data["message"]["items"]
    return items


def check_records(
    records: list[dict[str, Any]],
) -> tuple[list[Publication], list[tuple[Any, str]]]:
    """Делит записи на принятые (приведённые к Publication) и отклонённые."""
    accepted: list[Publication] = []
    rejected: list[tuple[Any, str]] = []
    for raw in records:
        try:
            work = CrossrefWork.model_validate(raw)
        except ValidationError as error:
            first = error.errors()[0]
            field_name = ".".join(str(p) for p in first["loc"])
            rejected.append((raw.get("DOI"), f"{field_name}: {first['msg']}"))
            continue

        try:
            accepted.append(to_publication(work))
        except ValueError as error:
            rejected.append((raw.get("DOI"), f"to_publication: {error}"))
    return accepted, rejected


def save_rejected(rejected: list[tuple[Any, str]], path: Path) -> None:
    """Записывает перечень отклонённых записей в файл CSV.

    Первая строка файла — заголовок doi,reason; далее по строке
    на каждую отклонённую запись.
    """
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["doi", "reason"])
        writer.writerows(rejected)


def to_publication(work: CrossrefWork) -> Publication:
    """Приводит запись CrossrefWork к объекту Publication.

    Бросает ValueError, если объект Publication не удаётся создать
    (например, пустое название).
    """
    authors = [
        " ".join(filter(None, [a.family, a.given]))
        for a in work.author
        if a.family or a.given
    ]

    issns: list[str] = []
    for raw_issn in work.issn:
        normalized = normalize_issn(raw_issn)
        if normalized is not None:
            issns.append(normalized)

    year: int | None = None
    if work.issued is not None and work.issued.date_parts:
        first = work.issued.date_parts[0]
        if first:
            year = first[0]

    journal_title = work.journal[0] if work.journal else None

    return Publication(
        title=work.title[0],
        year=year,
        doi=normalize_doi(work.doi),
        journal_title=journal_title,
        authors=authors,
        issns=issns,
    )


def find_duplicates(publications: list[Publication]) -> list[str]:
    """Возвращает DOI, встречающиеся более одного раза.

    Сравнение — по нормализованному DOI (None игнорируется).
    """
    counts = Counter(p.doi for p in publications if p.doi is not None)
    return [doi for doi, n in counts.items() if n > 1]


def openalex_to_publication(work: OpenAlexWork) -> Publication:
    """Приводит запись OpenAlexWork к объекту Publication."""
    issns: list[str] = []
    if work.primary_location and work.primary_location.source:
        source = work.primary_location.source
        candidates: list[str] = []
        if source.issn_l:
            candidates.append(source.issn_l)
        if source.issn:
            candidates.extend(source.issn)
        for raw in candidates:
            normalized = normalize_issn(raw)
            if normalized and normalized not in issns:
                issns.append(normalized)

    journal_title: str | None = None
    if work.primary_location and work.primary_location.source:
        journal_title = work.primary_location.source.display_name

    return Publication(
        title=work.title or "",
        year=work.publication_year,
        doi=normalize_doi(work.doi),
        journal_title=journal_title,
        authors=[],
        issns=issns,
    )
