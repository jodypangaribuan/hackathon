from math import isclose

from sipature_ml.config import load_config


def test_priority_weights_sum_to_one() -> None:
    weights = load_config("scoring")["priority_weights"]
    assert isclose(sum(weights.values()), 1.0)


def test_missing_data_is_not_treated_as_healthy() -> None:
    policy = load_config("scoring")["missing_data"]
    assert policy["never_treat_missing_as_healthy"] is True
