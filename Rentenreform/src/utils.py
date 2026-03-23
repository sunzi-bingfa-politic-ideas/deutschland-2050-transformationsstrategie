# Rentenreform/RSSP_v2/src/utils.py
from __future__ import annotations

from typing import List

import yaml


def frange(start: float, end: float, step: float, ndigits: int = 10) -> List[float]:
    """Inclusive float range with configurable rounding precision."""
    xs = []
    x = start
    while x <= end + 1e-12:
        xs.append(round(x, ndigits))
        x += step
    return xs


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
