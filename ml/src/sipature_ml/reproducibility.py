"""Deterministic seed setup shared by local scripts and Colab notebooks."""

from __future__ import annotations

import os
import random
from typing import Any

import numpy as np


def set_global_seed(seed: int) -> dict[str, Any]:
    """Seed Python, NumPy, and PyTorch when available.

    Returns the applied settings so callers can persist them in a run manifest.
    CUDA determinism can reduce performance and does not guarantee bitwise identity
    across hardware or library versions, which must also be recorded.
    """

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    settings: dict[str, Any] = {
        "seed": seed,
        "pythonhashseed": str(seed),
        "python_random": True,
        "numpy": True,
        "torch": False,
    }
    try:
        import torch
    except ImportError:
        return settings

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    settings["torch"] = True
    settings["cuda_available"] = torch.cuda.is_available()
    return settings
