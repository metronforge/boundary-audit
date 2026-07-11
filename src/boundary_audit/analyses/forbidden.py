"""Finite forbidden n-gram enumeration."""

from dataclasses import dataclass
from itertools import product

from boundary_audit.analyses.ngrams import NGramAnalysis, WindowMode
from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import AnalysisInputError
from boundary_audit.core.stream import SymbolStream


@dataclass(frozen=True, slots=True)
class ForbiddenNGramResult:
    """Possible, observed, and absent n-grams over the observed alphabet."""

    n: int
    mode: WindowMode
    possible_count: int
    observed_count: int
    forbidden: tuple[tuple[str, ...], ...]

    @property
    def forbidden_count(self) -> int:
        """Return the number of absent possible n-grams."""
        return len(self.forbidden)


@dataclass(frozen=True, slots=True)
class ForbiddenNGramAnalysis:
    """Enumerate absent words up to a strict universe-size limit."""

    n: int
    mode: WindowMode = "full"
    max_possible_ngrams: int = 1_000_000
    id = "forbidden_ngrams"
    version = "1"

    def __post_init__(self) -> None:
        if self.n < 1 or self.max_possible_ngrams < 1:
            raise AnalysisInputError("n and max_possible_ngrams must be positive")

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ForbiddenNGramResult:
        """Enumerate deterministically in first-observed alphabet order."""
        alphabet = stream.alphabet().symbols
        possible_count = len(alphabet) ** self.n
        if possible_count > self.max_possible_ngrams:
            raise AnalysisInputError(
                f"possible n-gram count {possible_count} exceeds limit "
                f"{self.max_possible_ngrams}"
            )
        observed = set(
            NGramAnalysis(self.n, self.mode).compute(stream, boundaries).counts
        )
        forbidden = tuple(
            word for word in product(alphabet, repeat=self.n) if word not in observed
        )
        return ForbiddenNGramResult(
            self.n, self.mode, possible_count, len(observed), forbidden
        )
