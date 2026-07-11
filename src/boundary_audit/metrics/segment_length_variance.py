"""Segment-length variance metric."""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import MetricInputError
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.base import ScalarMetricResult, validate_requirements
from boundary_audit.metrics.requirements import MetricRequirements


@dataclass(frozen=True, slots=True)
class SegmentLengthVarianceMetric:
    """Population or sample variance of complete segment lengths."""

    ddof: int = 0
    id = "segment_length_variance"
    version = "1"

    def __post_init__(self) -> None:
        if self.ddof < 0:
            raise MetricInputError("ddof must be non-negative")

    @property
    def requirements(self) -> MetricRequirements:
        """Require more segments than degrees of freedom."""
        return MetricRequirements(min_segment_count=self.ddof + 1)

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return the exact variance convention."""
        return {"ddof": self.ddof}

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None:
        """Validate stream, configuration, and sample size."""
        validate_requirements(self.requirements, stream, boundaries)

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult:
        """Compute variance in squared-symbol units."""
        self.validate_input(stream, boundaries)
        value = float(np.var(boundaries.segment_lengths(), ddof=self.ddof))
        return ScalarMetricResult(self.id, self.version, value, "symbols^2")
