"""N-gram counts with explicit boundary-window semantics."""

from collections import Counter
from dataclasses import dataclass
from typing import Literal

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import AnalysisInputError
from boundary_audit.core.stream import SymbolStream

WindowMode = Literal["full", "within", "across"]


def eligible_starts(
    stream_length: int, boundaries: BoundaryConfiguration, n: int, mode: WindowMode
) -> tuple[int, ...]:
    """Return starts whose internal gaps satisfy the requested mode."""
    if n < 1:
        raise AnalysisInputError("n must be at least 1")
    if mode not in ("full", "within", "across"):
        raise AnalysisInputError(f"unknown window mode {mode!r}")
    if stream_length != boundaries.stream_length:
        raise AnalysisInputError("stream and configuration lengths differ")
    present = set(boundaries.positions)
    starts: list[int] = []
    for start in range(max(0, stream_length - n + 1)):
        crosses = any(position in present for position in range(start + 1, start + n))
        if (
            mode == "full"
            or (mode == "within" and not crosses)
            or (mode == "across" and crosses)
        ):
            starts.append(start)
    return tuple(starts)


@dataclass(frozen=True, slots=True)
class NGramResult:
    """Deterministically ordered n-gram counts."""

    n: int
    mode: WindowMode
    counts: dict[tuple[str, ...], int]
    sample_count: int


@dataclass(frozen=True, slots=True)
class NGramAnalysis:
    """Count n-grams under full, within, or across semantics."""

    n: int
    mode: WindowMode = "full"
    id = "ngram_frequency"
    version = "1"

    def __post_init__(self) -> None:
        if self.n < 1:
            raise AnalysisInputError("n must be at least 1")

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> NGramResult:
        """Return lexicographically ordered tuple-keyed counts."""
        starts = eligible_starts(len(stream), boundaries, self.n, self.mode)
        counter = Counter(stream.symbols[start : start + self.n] for start in starts)
        return NGramResult(
            self.n, self.mode, dict(sorted(counter.items())), len(starts)
        )
