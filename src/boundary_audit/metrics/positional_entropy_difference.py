"""Initial/final segment-symbol entropy difference."""

from collections.abc import Mapping
from dataclasses import dataclass

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.base import ScalarMetricResult, validate_requirements
from boundary_audit.metrics.requirements import MetricRequirements
from boundary_audit.utils.numeric import entropy_bits


@dataclass(frozen=True, slots=True)
class PositionalEntropyResult:
    """Structured initial and final entropy values."""

    initial_entropy: float
    final_entropy: float
    absolute_difference: float


def positional_entropies(
    stream: SymbolStream, boundaries: BoundaryConfiguration
) -> PositionalEntropyResult:
    """Return entropy of first and last symbols across all segments."""
    segments = boundaries.segments(stream)
    initial = entropy_bits(tuple(segment[0] for segment in segments))
    final = entropy_bits(tuple(segment[-1] for segment in segments))
    return PositionalEntropyResult(initial, final, abs(initial - final))


@dataclass(frozen=True, slots=True)
class PositionalEntropyDifferenceMetric:
    """Absolute initial-versus-final symbol entropy difference."""

    id = "positional_entropy_difference"
    version = "1"
    requirements = MetricRequirements(min_segment_count=2)

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return the base and absolute-difference convention."""
        return {"log_base": 2, "statistic": "absolute_difference"}

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None:
        """Require at least two complete segments."""
        validate_requirements(self.requirements, stream, boundaries)

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult:
        """Compute the absolute difference in bits."""
        self.validate_input(stream, boundaries)
        result = positional_entropies(stream, boundaries)
        return ScalarMetricResult(
            self.id, self.version, result.absolute_difference, "bits"
        )
