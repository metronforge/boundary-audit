"""One-sided Parseval-consistent spectral analyses."""

import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import AnalysisInputError
from boundary_audit.core.stream import SymbolStream

Detrend = Literal["none", "mean"]


@dataclass(frozen=True, slots=True)
class SpectrumResult:
    """One-sided frequencies, power, entropy, and dominant bins."""

    frequencies: tuple[float, ...]
    power: tuple[float, ...]
    dominant_frequencies: tuple[float, ...]
    spectral_entropy: float
    units: str
    detrend: Detrend


def power_spectrum(
    values: tuple[float, ...], *, top_k: int = 5, detrend: Detrend = "mean", units: str
) -> SpectrumResult:
    """Compute one-sided power whose sum equals mean-square signal power."""
    if not values:
        raise AnalysisInputError("spectral analysis requires at least one value")
    if top_k < 0 or detrend not in ("none", "mean"):
        raise AnalysisInputError("top_k must be non-negative and detrend valid")
    x = np.asarray(values, dtype=np.float64)
    if detrend == "mean":
        x = x - np.mean(x)
    n = len(x)
    transformed = np.fft.rfft(x)
    power = np.abs(transformed) ** 2 / (n * n)
    if n > 1:
        if n % 2 == 0:
            power[1:-1] *= 2.0
        else:
            power[1:] *= 2.0
    frequencies = np.fft.rfftfreq(n, d=1.0)
    eligible = np.arange(1, len(power)) if detrend == "mean" else np.arange(len(power))
    positive = eligible[power[eligible] > 0.0]
    total = float(np.sum(power[positive]))
    if total == 0.0:
        entropy = 0.0
        dominant: tuple[float, ...] = ()
    else:
        mass = power[positive] / total
        raw_entropy = -float(np.sum(mass * np.log2(mass)))
        entropy = raw_entropy / math.log2(len(positive)) if len(positive) > 1 else 0.0
        ranked = sorted(positive, key=lambda index: (-power[index], frequencies[index]))
        dominant = tuple(float(frequencies[index]) for index in ranked[:top_k])
    return SpectrumResult(
        tuple(float(value) for value in frequencies),
        tuple(float(value) for value in power),
        dominant,
        entropy,
        units,
        detrend,
    )


@dataclass(frozen=True, slots=True)
class BoundarySpectrumAnalysis:
    """Spectrum of the length n-1 boundary indicator."""

    top_k: int = 5
    detrend: Detrend = "mean"
    id = "boundary_spectrum"
    version = "1"

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> SpectrumResult:
        """Compute cycles per symbol gap under a rectangular window."""
        if len(stream) != boundaries.stream_length or len(stream) < 2:
            raise AnalysisInputError(
                "boundary spectrum requires a matching length >= 2"
            )
        return power_spectrum(
            tuple(float(value) for value in boundaries.to_indicator()),
            top_k=self.top_k,
            detrend=self.detrend,
            units="cycles per symbol gap",
        )


@dataclass(frozen=True, slots=True)
class SegmentLengthSpectrumAnalysis:
    """Spectrum of the complete segment-length sequence."""

    top_k: int = 5
    detrend: Detrend = "mean"
    id = "segment_length_spectrum"
    version = "1"

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> SpectrumResult:
        """Compute cycles per segment under a rectangular window."""
        if len(stream) != boundaries.stream_length:
            raise AnalysisInputError("stream and configuration lengths differ")
        return power_spectrum(
            tuple(float(value) for value in boundaries.segment_lengths()),
            top_k=self.top_k,
            detrend=self.detrend,
            units="cycles per segment",
        )
