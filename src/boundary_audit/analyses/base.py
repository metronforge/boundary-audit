"""Structured-analysis protocol."""

from typing import Protocol, TypeVar

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream

TResult_co = TypeVar("TResult_co", covariant=True)


class Analysis(Protocol[TResult_co]):
    """A structured computation that is not a scalar test statistic."""

    id: str
    version: str

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> TResult_co:
        """Compute a structured result."""
        ...
