"""Forbidden n-gram fraction metric."""

from collections.abc import Mapping
from dataclasses import dataclass

from boundary_audit.analyses.forbidden import ForbiddenNGramAnalysis
from boundary_audit.analyses.ngrams import WindowMode
from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.base import ScalarMetricResult, validate_requirements
from boundary_audit.metrics.requirements import MetricRequirements


@dataclass(frozen=True, slots=True)
class ForbiddenNGramFractionMetric:
    """Absent fraction of the finite observed-alphabet n-gram universe."""

    n: int = 2
    mode: WindowMode = "full"
    max_possible_ngrams: int = 1_000_000
    id = "forbidden_ngram_fraction"
    version = "1"
    requirements = MetricRequirements()

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return enumeration parameters."""
        return {
            "n": self.n,
            "mode": self.mode,
            "max_possible_ngrams": self.max_possible_ngrams,
        }

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None:
        """Validate common and analysis-specific preconditions."""
        validate_requirements(self.requirements, stream, boundaries)
        ForbiddenNGramAnalysis(self.n, self.mode, self.max_possible_ngrams)

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult:
        """Compute forbidden_count divided by possible_count."""
        self.validate_input(stream, boundaries)
        result = ForbiddenNGramAnalysis(
            self.n, self.mode, self.max_possible_ngrams
        ).compute(stream, boundaries)
        return ScalarMetricResult(
            self.id,
            self.version,
            result.forbidden_count / result.possible_count,
            "fraction",
        )
