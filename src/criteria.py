"""Критерии проверки публикаций: описание и загрузка."""

import tomllib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Criteria(BaseModel):
    """Критерии из локального нормативного акта."""

    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    basis: str = Field(min_length=1)  # ссылка на локальный акт
    year_from: int  # начало отчётного периода
    year_to: int  # конец отчётного периода
    max_level: int = Field(ge=1, le=4)  # пороговый уровень издания
    registry_version: str = Field(min_length=1)  # версия справочника изданий

    @model_validator(mode="after")
    def check_period(self) -> "Criteria":
        """Проверяет корректность отчётного периода."""
        if self.year_from > self.year_to:
            raise ValueError("year_from не может быть больше year_to")
        return self


def load_criteria(path: Path) -> Criteria:
    """Читает критерии из файла и проверяет их."""
    with path.open("rb") as file:
        data = tomllib.load(file)
    return Criteria.model_validate(data["criteria"])
