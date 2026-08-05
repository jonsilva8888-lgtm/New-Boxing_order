"""Utility helpers."""
from __future__ import annotations
import random
from typing import Iterable, TypeVar
T = TypeVar('T')

def clamp(value: float, low: float = 1, high: float = 100) -> int:
    return int(max(low, min(high, round(value))))

def weighted_choice(items: list[tuple[T, float]]) -> T:
    total = sum(max(0, w) for _, w in items)
    if total <= 0:
        return random.choice([i for i, _ in items])
    pick = random.uniform(0, total)
    upto = 0.0
    for item, weight in items:
        upto += max(0, weight)
        if upto >= pick:
            return item
    return items[-1][0]

def money(amount: int) -> str:
    return f"${amount:,.0f}"
