"""Declarative scalar-metric input and null-model requirements."""

from dataclasses import dataclass

from boundary_audit.null_models.base import BoundaryInvariant


@dataclass(frozen=True, slots=True)
class MetricRequirements:
    """Static requirements checked before Monte Carlo sampling."""

    min_stream_length: int = 1
    min_boundary_count: int = 0
    min_segment_count: int = 1
    required_null_invariants: frozenset[BoundaryInvariant] = frozenset()
