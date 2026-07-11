"""Finite-sample block complexity."""

import math
from dataclasses import dataclass

from boundary_audit.analyses.ngrams import NGramAnalysis, WindowMode
from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import AnalysisInputError
from boundary_audit.core.stream import SymbolStream


@dataclass(frozen=True, slots=True)
class FiniteSampleBlockComplexity:
    """The finite quantity log2 of observed language size divided by n."""

    n: int
    mode: WindowMode
    distinct_count: int
    value: float


@dataclass(frozen=True, slots=True)
class BlockComplexityAnalysis:
    """Compute finite-sample block complexity without entropy claims."""

    n: int
    mode: WindowMode = "full"
    id = "finite_sample_block_complexity"
    version = "1"

    def __post_init__(self) -> None:
        if self.n < 1:
            raise AnalysisInputError("n must be at least 1")

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> FiniteSampleBlockComplexity:
        """Return zero when no eligible block is observed."""
        count = len(NGramAnalysis(self.n, self.mode).compute(stream, boundaries).counts)
        value = math.log2(count) / self.n if count else 0.0
        return FiniteSampleBlockComplexity(self.n, self.mode, count, value)
