import random

import numpy as np

from sipature_ml.reproducibility import set_global_seed


def test_global_seed_repeats_python_and_numpy_sequences() -> None:
    first_settings = set_global_seed(42)
    first = (random.random(), np.random.random())
    second_settings = set_global_seed(42)
    second = (random.random(), np.random.random())
    assert first == second
    assert first_settings["seed"] == second_settings["seed"] == 42
