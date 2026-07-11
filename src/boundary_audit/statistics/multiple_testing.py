"""Pure Holm and Benjamini-Hochberg adjustments."""

import math
from collections.abc import Sequence

from boundary_audit.core.errors import MetricInputError


def _validate(p_values: Sequence[float]) -> tuple[float, ...]:
    values = tuple(float(value) for value in p_values)
    if any(not math.isfinite(value) or not 0.0 <= value <= 1.0 for value in values):
        raise MetricInputError("p-values must be finite and lie in [0, 1]")
    return values


def holm_adjust(p_values: Sequence[float]) -> tuple[float, ...]:
    """Return Holm family-wise adjusted p-values in input order."""
    values = _validate(p_values)
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [0.0] * len(values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(values) - rank) * values[index])
        adjusted[index] = min(1.0, running)
    return tuple(adjusted)


def benjamini_hochberg_adjust(p_values: Sequence[float]) -> tuple[float, ...]:
    """Return BH false-discovery-rate adjusted p-values in input order."""
    values = _validate(p_values)
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [0.0] * len(values)
    running = 1.0
    for rank in range(len(values), 0, -1):
        index = order[rank - 1]
        running = min(running, len(values) * values[index] / rank)
        adjusted[index] = min(1.0, running)
    return tuple(adjusted)
