"""Order-one and order-two empirical transitions."""

from collections import Counter, defaultdict
from dataclasses import dataclass

from boundary_audit.analyses.ngrams import WindowMode, eligible_starts
from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import AnalysisInputError
from boundary_audit.core.stream import SymbolStream


@dataclass(frozen=True, slots=True)
class TransitionResult:
    """Counts and non-empty row-normalized transition probabilities."""

    order: int
    mode: WindowMode
    counts: dict[tuple[str, ...], dict[str, int]]
    probabilities: dict[tuple[str, ...], dict[str, float]]
    sample_count: int


@dataclass(frozen=True, slots=True)
class TransitionAnalysis:
    """Compute empirical transitions with contexts of length one or two."""

    order: int = 1
    mode: WindowMode = "full"
    id = "transitions"
    version = "1"

    def __post_init__(self) -> None:
        if self.order not in (1, 2):
            raise AnalysisInputError("transition order must be 1 or 2")

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> TransitionResult:
        """Compute deterministic nested mappings."""
        starts = eligible_starts(len(stream), boundaries, self.order + 1, self.mode)
        mutable: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
        for start in starts:
            context = stream.symbols[start : start + self.order]
            mutable[context][stream.symbols[start + self.order]] += 1
        counts = {
            context: dict(sorted(row.items()))
            for context, row in sorted(mutable.items())
        }
        probabilities = {
            context: {
                target: count / sum(row.values()) for target, count in row.items()
            }
            for context, row in counts.items()
        }
        return TransitionResult(
            self.order, self.mode, counts, probabilities, len(starts)
        )
