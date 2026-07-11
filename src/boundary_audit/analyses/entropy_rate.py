"""Finite empirical conditional-entropy profiles."""

import math
from dataclasses import dataclass

from boundary_audit.analyses.ngrams import WindowMode
from boundary_audit.analyses.transitions import TransitionAnalysis
from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import AnalysisInputError
from boundary_audit.core.stream import SymbolStream


@dataclass(frozen=True, slots=True)
class ConditionalEntropyResult:
    """Empirical plug-in conditional entropy in bits."""

    order: int
    mode: WindowMode
    entropy_bits: float
    sample_count: int


@dataclass(frozen=True, slots=True)
class ConditionalEntropyAnalysis:
    """Compute H(target | context) for context order one or two."""

    order: int = 1
    mode: WindowMode = "full"
    min_observations: int = 10
    id = "conditional_entropy"
    version = "1"

    def __post_init__(self) -> None:
        if self.order not in (1, 2) or self.min_observations < 1:
            raise AnalysisInputError(
                "order must be 1 or 2 and min_observations positive"
            )

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ConditionalEntropyResult:
        """Return the weighted entropy of non-empty transition rows."""
        result = TransitionAnalysis(self.order, self.mode).compute(stream, boundaries)
        if result.sample_count < self.min_observations:
            raise AnalysisInputError(
                f"requires at least {self.min_observations} eligible windows"
            )
        entropy = 0.0
        for row in result.counts.values():
            row_total = sum(row.values())
            row_entropy = -sum(
                (count / row_total) * math.log2(count / row_total)
                for count in row.values()
            )
            entropy += (row_total / result.sample_count) * row_entropy
        return ConditionalEntropyResult(
            self.order, self.mode, entropy, result.sample_count
        )
