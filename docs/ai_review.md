# Разбор кода, предложенного ИИ-ассистентом

**Файл:** `sandbox/ai_publication.py`.
**Проверки исполнением:** `uv run python sandbox/check_ai.py`.
**Статический анализ:** `uv run mypy sandbox/ai_publication.py`.


| № | Фрагмент кода | Вопрос проверки (табл. 2.2) | К чему приводит и как подтверждено | Исправление |
|---|---------------|-----------------------------|-------------------------------------|-------------|
| 1 | В классе нет поля `journal_title` | Все ли свойства сущности учтены? | В таблице 2.3 у публикации есть **название издания** — без него нельзя проверить уровень в ЕГПНИ. Подтверждено: `check_missing_journal_title()` → `'journal_title' присутствует: False` | Добавить поле `journal_title: str \| None = None` |
| 2 | `same_publication` сравнивает только `title` | Все ли свойства сущности учтены? | По таблице 2.3 публикацию идентифицируют не только название, но и DOI, ISSN, авторы, год. Две разные публикации с одинаковым названием будут считаться одной. Подтверждено: `check_same_publication_only_title()` → `True` для DOI `10.5555/a` и `10.5555/b` | Сравнивать сначала по нормализованному DOI, затем по ISSN+год, название — вспомогательный признак |
| 3 | `year: str` | Ограничены ли допустимые значения? | Год — целое число 1900…2100, но `str` принимает `"двадцать пятый"`, `"abc"`, `" "`. Подтверждено: `check_year_type()` → `year = 'двадцать пятый'` | `year: int \| None` + проверка 1900…2100 в `__post_init__` |
| 4 | `title: str` без проверки | Ограничены ли допустимые значения? | Название — обязательное непустое поле, но принимаются `""` и `"   "`. Подтверждено: `check_title_empty()` → оба пустых объекта созданы | `if not self.title.strip(): raise ValueError(...)` в `__post_init__` |
| 5 | `doi: str = ""` | Как обозначено отсутствие значения? | Пустая строка — допустимое значение; «DOI не указан» смешивается с «DOI указан пустой строкой». Подтверждено: `check_doi_empty_string()` → `p1.doi == p2.doi → True` | `doi: str \| None = None` |
| 6 | `issn: str = ""` | Как обозначено отсутствие значения? | То же: пустая строка вместо `None`. Подтверждено: `check_issn_empty_string()` → `issn = ''` | `issns: list[str] = field(default_factory=list)` |
| 7 | `authors: str  # через запятую` | Учтена ли множественность значений? | У публикации может быть несколько авторов; запись через запятую ломается, если в ФИО есть запятая, и не даёт числа авторов. Подтверждено: `check_authors_multiplicity()` | `authors: list[str] = field(default_factory=list)` |
| 8 | `issn: str` | Учтена ли множественность значений? | В таблице 2.3 ISSN — множественное свойство; у издания бывает печатный и электронный ISSN. Подтверждено: `check_issn_multiplicity()` → второй ISSN задать некуда | `issns: list[str] = field(default_factory=list)` |
| 9 | `a.title.normalize()` в `same_publication` | Существуют ли упомянутые функции и параметры? | У `str` нет метода `normalize`; функция падает на **любом** вызове. Подтверждено: `check_normalize_method()` → `AttributeError`; `uv run mypy sandbox/ai_publication.py` → `error: "str" has no attribute "normalize" [attr-defined]` | Реализовать `normalize_title()` в `src/normalize.py`; вызвать её |

## Итог

Найдено **9 ошибок**. 

| Вопрос | Ошибки |
|---|---|
| Все ли свойства сущности учтены? | №1, №2 |
| Ограничены ли допустимые значения? | №3, №4 |
| Как обозначено отсутствие значения? | №5, №6 |
| Учтена ли множественность значений? | №7, №8 |
| Существуют ли упомянутые функции и параметры? | №9 |


# Разбор собственной модели от ИИ-ассистента

**Запрос (отправлен ИИ-ассистенту):**

> Опиши на Python модель данных для системы проверки научных публикаций.
> Публикация должна содержать: название, авторов, год выхода, DOI,
> ISSN, название издания. Авторов может быть несколько, ISSN тоже может
> быть несколько (печатный и электронный). Отсутствие значения нужно
> обозначать явно. Используй dataclasses и перечисления, где это уместно.
> Также добавь функцию, которая определяет, описывают ли две записи
> одну и ту же публикацию.

**Ответ ИИ-ассистента (фрагмент):**

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ISSType(Enum):
    """Тип ISSN."""
    PRINT = "print"
    ELECTRONIC = "electronic"


@dataclass(frozen=True)
class Author:
    """Автор публикации.

    Fields:
        name: ФИО автора.
        orcid: Идентификатор ORCID (уникальный цифровой код исследователя).
        affiliation: Название организации, с которой автор связан.
    """
    name: str
    orcid: Optional[str] = None
    affiliation: Optional[str] = None


@dataclass(frozen=True)
class ISSN:
    """ISSN издания с указанием типа.

    Fields:
        value: Значение ISSN в формате XXXX-XXXX.
        type: Тип ISSN (печатный или электронный).
    """
    value: str
    type: ISSType


@dataclass(frozen=True)
class Publication:
    """Научная публикация.

    Fields:
        title: Название публикации.
        authors: Список авторов (может быть пустым).
        year: Год выхода.
        doi: DOI публикации (уникальный идентификатор).
        issns: Список ISSN издания (печатный и/или электронный).
        venue: Название издания (журнал, конференция, сборник).
    """
    title: str
    authors: list[Author] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    issns: list[ISSN] = field(default_factory=list)
    venue: Optional[str] = None

    def authors_str(self) -> str:
        """Возвращает строку со всеми авторами через запятую."""
        return ", ".join(a.name for a in self.authors)


def _normalize(text: Optional[str]) -> Optional[str]:
    """Нормализует строку: нижний регистр, удаление лишних пробелов."""
    if text is None:
        return None
    return " ".join(text.strip().lower().split())


def _normalize_issn(value: str) -> str:
    """Приводит ISSN к стандартному виду XXXX-XXXX в верхнем регистре."""
    cleaned = value.strip().upper().replace(" ", "")
    if "-" not in cleaned and len(cleaned) == 8:
        return f"{cleaned[:4]}-{cleaned[4:]}"
    return cleaned


def is_same_publication(a: Publication, b: Publication) -> bool:
    """Определяет, описывают ли две записи одну и ту же публикацию.

    Проверка выполняется по уровням убывания надёжности:
      1. Совпадение DOI (если есть у обеих) — самый сильный признак.
      2. Совпадение хотя бы одного ISSN, названия издания, года
         и нормализованного названия.
      3. Совпадение нормализованного названия, года и состава авторов
         (фамилии).
    """
    # --- 1. Совпадение по DOI ---
    if a.doi is not None and b.doi is not None:
        return a.doi.strip().lower() == b.doi.strip().lower()

    # --- 2. Совпадение по ISSN + издание + год + название ---
    a_issns = {_normalize_issn(i.value) for i in a.issns}
    b_issns = {_normalize_issn(i.value) for i in b.issns}

    if a_issns and b_issns and a_issns & b_issns:
        same_venue = _normalize(a.venue) == _normalize(b.venue)
        same_year = a.year == b.year
        same_title = _normalize(a.title) == _normalize(b.title)
        if same_venue and same_year and same_title:
            return True

    # --- 3. Совпадение по названию + году + авторам (фамилии) ---
    same_title = _normalize(a.title) == _normalize(b.title)
    same_year = a.year == b.year
    a_surnames = {a_.name.split()[-1].lower() for a_ in a.authors}
    b_surnames = {b_.name.split()[-1].lower() for b_ in b.authors}
    same_authors = bool(a_surnames) and a_surnames == b_surnames

    if same_title and same_year and same_authors:
        return True

    return False
```

**Разбор:**

| № | Фрагмент кода ИИ | Вопрос проверки (табл. 2.2) | Расхождение | Исправление |
|---|------------------|-----------------------------|-------------|-------------|
| 1 | `venue: Optional[str]` | Все ли свойства сущности учтены? | По таблице 2.3 поле должно называться `journal_title`. Методичка (п. 4.3) требует не менять имена полей | Переименовать в `journal_title: str \| None = None` |
| 2 | Отсутствует `__post_init__` | Ограничены ли допустимые значения? | `title` может быть пустой строкой или строкой из пробелов — не отклоняется | Добавить `__post_init__`: `if not self.title.strip(): raise ValueError(...)` |
| 3 | Отсутствует проверка `year` | Ограничены ли допустимые значения? | По таблице 2.3 год должен быть в диапазоне 1900…2100. У ИИ проверки нет | В `__post_init__`: `if self.year is not None and not (1900 <= self.year <= 2100): raise ValueError(...)` |
| 4 | `_normalize_issn` возвращает `"0040-6090"` | Ограничены ли допустимые значения? | По таблице 2.4 ISSN нормализуется к 8 символам без дефиса — `"00406090"` | Использовать `normalize_issn` из `src/normalize.py` |
| 5 | Контрольный разряд ISSN не проверяется | Ограничены ли допустимые значения? | ISSN `2071-2457` проходит форматирование, хотя контрольная сумма не сходится | Вызывать `issn_check_digit_ok(issn)` из `src/normalize.py` |
| 6 | `authors: list[Author]` | Учтена ли множественность значений? | Множественность учтена, но тип не соответствует таблице 2.3 — там «Список строк», а не список объектов `Author` | `authors: list[str] = field(default_factory=list)` |
| 7 | `issns: list[ISSN]` | Учтена ли множественность значений? | То же — по таблице 2.3 «Список строк», а не список объектов `ISSN` | `issns: list[str] = field(default_factory=list)` |
| 8 | В `is_same_publication`: `a_.name.split()[-1]` | Существуют ли упомянутые функции и параметры? | Если у автора пустое имя (`name = ""`), `.split()` вернёт пустой список — `[-1]` выбросит `IndexError` | Проверять `name.strip()` перед `.split()[-1]` |

**Итог:** найдено **8 расхождений** с требованиями таблицы 2.3.

**Что ИИ сделал хорошо:**

- все 6 свойств сущности присутствуют;
- отсутствие `year`, `doi`, `journal_title` обозначено через `None` — верно;
- `authors` и `issns` объявлены с `field(default_factory=list)` — правильно;
- есть функция сравнения `is_same_publication` с продуманной логикой.

**Распределение расхождений по вопросам таблицы 2.2:**

| Вопрос | Номера ошибок |
|---|---|
| Все ли свойства сущности учтены? | 1 |
| Ограничены ли допустимые значения? | 2, 3, 4, 5 |
| Как обозначено отсутствие значения? | — (всё верно) |
| Учтена ли множественность значений? | 6, 7 |
| Существуют ли упомянутые функции и параметры? | 8 |