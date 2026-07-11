"""Empirical add-one p-values and effect summaries."""

import math
from collections.abc import Sequence
from typing import Literal

import numpy as np

from boundary_audit.core.errors import MetricInputError

Alternative = Literal["greater", "less", "two-sided"]


def empirical_p_value(
    observed: float, null_values: Sequence[float], alternative: Alternative
) -> float:
    """Compute the specified add-one empirical p-value."""
    if not null_values:
        raise MetricInputError("at least one null value is required")
    if alternative not in ("greater", "less", "two-sided"):
        raise MetricInputError(f"unknown alternative {alternative!r}")
    values = np.asarray(null_values, dtype=np.float64)
    if alternative == "greater":
        count = int(np.count_nonzero(values >= observed))
    elif alternative == "less":
        count = int(np.count_nonzero(values <= observed))
    else:
        mean = float(np.mean(values))
        count = int(np.count_nonzero(np.abs(values - mean) >= abs(observed - mean)))
    return (1 + count) / (len(values) + 1)


def z_score(observed: float, null_mean: float, null_std: float) -> float:
    """Compute z, including the specified zero-variance convention."""
    effect = observed - null_mean
    if null_std == 0.0:
        return 0.0 if effect == 0.0 else math.copysign(math.inf, effect)
    return effect / null_std
