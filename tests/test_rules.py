import pytest

from src.criteria import Criteria
from src.models import Decision
from src.rules import decide

RULES = Criteria(
    basis="тестовый пример",
    year_from=2025,
    year_to=2026,
    max_level=2,
    registry_version="тестовая версия",
)


CASES = [
    (2025, 1, Decision.ACCEPTED),
    (2026, 2, Decision.ACCEPTED),
    (2025, 3, Decision.REJECTED),
    (2024, 1, Decision.REJECTED),
    (2027, 1, Decision.REJECTED),
    (2025, None, Decision.MANUAL),
    (2024, None, Decision.REJECTED),
]


@pytest.mark.parametrize(("year", "level", "expected"), CASES)
def test_decide(year: int, level: int | None, expected: Decision) -> None:
    assert decide(year, level, RULES) == expected
