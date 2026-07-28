import pandas as pd

from sipature_ml.eda import _parse_coordinate, _parse_rating, profile_ngrams


def test_parse_rating_handles_decimal_comma_and_rejects_nonrating() -> None:
    assert _parse_rating("4,5") == 4.5
    assert _parse_rating("4.5") == 4.5
    assert _parse_rating("10,000") is None
    assert _parse_rating("") is None


def test_parse_coordinate_handles_spacing_and_range() -> None:
    assert _parse_coordinate("2.35, 99.07") == (2.35, 99.07)
    assert _parse_coordinate("2.35,99.07") == (2.35, 99.07)
    assert _parse_coordinate("95, 99") is None
    assert _parse_coordinate("83XF+9VQ") is None


def test_profile_ngrams_returns_all_three_sizes() -> None:
    result = profile_ngrams(pd.Series(["jalan rusak parah", "jalan rusak sekali", "tempat bagus sekali"]))
    assert set(result["n"]) == {1, 2, 3}
