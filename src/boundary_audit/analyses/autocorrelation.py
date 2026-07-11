"""Biased autocorrelation with an explicit lag-zero convention."""

from dataclasses import dataclass
from typing import Literal

import numpy as np

from boundary_audit.core.errors import AnalysisInputError


@dataclass(frozen=True, slots=True)
class AutocorrelationResult:
    """Lags and mean-centered autocovariance values."""

    lags: tuple[int, ...]
    values: tuple[float, ...]
    normalization: Literal["biased"]


def autocorrelation(
    x: tuple[float, ...],
    max_lag: int | None = None,
    normalization: Literal["biased"] = "biased",
) -> AutocorrelationResult:
    """Return biased autocovariance; lag zero is population variance."""
    if not x or normalization != "biased":
        raise AnalysisInputError(
            "x must be non-empty and normalization must be 'biased'"
        )
    n = len(x)
    limit = n - 1 if max_lag is None else max_lag
    if limit < 0 or limit >= n:
        raise AnalysisInputError("max_lag must lie in 0..len(x)-1")
    values = np.asarray(x, dtype=np.float64)
    values -= np.mean(values)
    correlations = tuple(
        float(np.dot(values[: n - lag], values[lag:]) / n) for lag in range(limit + 1)
    )
    return AutocorrelationResult(tuple(range(limit + 1)), correlations, normalization)
