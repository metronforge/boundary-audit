"""Boundary/pair plug-in mutual information."""

import math
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.base import ScalarMetricResult, validate_requirements
from boundary_audit.metrics.requirements import MetricRequirements


@dataclass(frozen=True, slots=True)
class BoundaryPairMutualInformationMetric:
    """Empirical I(boundary indicator; adjacent symbol pair) in bits."""

    id = "boundary_pair_mutual_information"
    version = "1"
    requirements = MetricRequirements(min_stream_length=2)

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return plug-in and sample-universe conventions."""
        return {"estimator": "empirical_plugin", "log_base": 2}

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None:
        """Require at least one adjacent gap."""
        validate_requirements(self.requirements, stream, boundaries)

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult:
        """Compute mutual information over exactly n-1 gaps."""
        self.validate_input(stream, boundaries)
        indicators = boundaries.to_indicator()
        pairs = tuple(zip(stream.symbols, stream.symbols[1:], strict=False))
        joint = Counter(zip(indicators, pairs, strict=True))
        x_counts = Counter(indicators)
        pair_counts = Counter(pairs)
        total = len(indicators)
        value = 0.0
        for (indicator, pair), count in joint.items():
            probability = count / total
            value += probability * math.log2(
                probability
                / ((x_counts[indicator] / total) * (pair_counts[pair] / total))
            )
        return ScalarMetricResult(self.id, self.version, value, "bits")
