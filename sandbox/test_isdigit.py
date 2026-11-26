from hypothesis import given
from hypothesis import strategies as st

from sandbox.isdigit_issn import normalize_issn

# символ, который Юникод относит к десятичным цифрам
digit = st.characters(categories=["Nd"])


@given(st.text(digit, min_size=8, max_size=8))
def test_only_ascii_digits_accepted(value: str) -> None:
    result = normalize_issn(value)
    assert result is None or result.isascii()
