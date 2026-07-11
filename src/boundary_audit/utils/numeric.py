"""Shared numerical conventions."""

import math
from collections import Counter
from collections.abc import Sequence


def entropy_bits(values: Sequence[object]) -> float:
    """Return empirical plug-in entropy in bits; empty input has entropy zero."""
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())
