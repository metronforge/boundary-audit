"""Scalar-metric protocol and result."""

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import MetricInputError, NonFiniteMetricError
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.requirements import MetricRequirements


@dataclass(frozen=True, slots=True)
class ScalarMetricResult:
    """One predeclared scalar test statistic."""

    metric_id: str
    metric_version: str
    value: float
    units: str

    def __post_init__(self) -> None:
        if not math.isfinite(self.value):
            raise NonFiniteMetricError("scalar metric value must be finite")


class ScalarMetric(Protocol):
    """Protocol accepted by the null-comparison runner."""

    id: str
    version: str

    @property
    def requirements(self) -> MetricRequirements: ...

    def parameters(self) -> Mapping[str, JSONValue]: ...

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None: ...

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult: ...


def validate_requirements(
    requirements: MetricRequirements,
    stream: SymbolStream,
    boundaries: BoundaryConfiguration,
) -> None:
    """Enforce common metric preconditions."""
    if len(stream) != boundaries.stream_length:
        raise MetricInputError("stream and configuration lengths differ")
    if len(stream) < requirements.min_stream_length:
        raise MetricInputError(
            f"metric requires stream length >= {requirements.min_stream_length}"
        )
    if boundaries.count < requirements.min_boundary_count:
        raise MetricInputError(
            f"metric requires boundary count >= {requirements.min_boundary_count}"
        )
    if boundaries.segment_count < requirements.min_segment_count:
        raise MetricInputError(
            f"metric requires segment count >= {requirements.min_segment_count}"
        )
