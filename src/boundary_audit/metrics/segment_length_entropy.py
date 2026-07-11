"""Segment-length entropy metric."""

from collections.abc import Mapping
from dataclasses import dataclass

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.base import ScalarMetricResult, validate_requirements
from boundary_audit.metrics.requirements import MetricRequirements
from boundary_audit.utils.numeric import entropy_bits


@dataclass(frozen=True, slots=True)
class SegmentLengthEntropyMetric:
    """Empirical entropy of the complete segment-length distribution."""

    id = "segment_length_entropy"
    version = "1"
    requirements = MetricRequirements()

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return the base-two convention."""
        return {"log_base": 2}

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None:
        """Validate common preconditions."""
        validate_requirements(self.requirements, stream, boundaries)

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult:
        """Compute entropy in bits."""
        self.validate_input(stream, boundaries)
        return ScalarMetricResult(
            self.id,
            self.version,
            entropy_bits(boundaries.segment_lengths()),
            "bits",
        )
