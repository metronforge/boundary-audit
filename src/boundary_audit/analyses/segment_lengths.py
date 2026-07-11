"""Structured segment-length summary."""

from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import AnalysisInputError
from boundary_audit.core.stream import SymbolStream


@dataclass(frozen=True, slots=True)
class SegmentLengthSummary:
    """Exact lengths and common descriptive statistics."""

    lengths: tuple[int, ...]
    count: int
    mean: float
    variance: float
    minimum: int
    maximum: int


@dataclass(frozen=True, slots=True)
class SegmentLengthAnalysis:
    """Summarize all implied segment lengths."""

    id = "segment_lengths"
    version = "1"

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> SegmentLengthSummary:
        """Compute a population-variance summary."""
        if len(stream) != boundaries.stream_length:
            raise AnalysisInputError("stream and configuration lengths differ")
        lengths = boundaries.segment_lengths()
        return SegmentLengthSummary(
            lengths,
            len(lengths),
            float(np.mean(lengths)),
            float(np.var(lengths)),
            min(lengths),
            max(lengths),
        )
