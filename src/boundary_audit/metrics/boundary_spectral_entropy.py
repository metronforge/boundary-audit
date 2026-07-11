"""Normalized boundary-indicator spectral entropy metric."""

from collections.abc import Mapping
from dataclasses import dataclass

from boundary_audit.analyses.spectra import BoundarySpectrumAnalysis, Detrend
from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.base import ScalarMetricResult, validate_requirements
from boundary_audit.metrics.requirements import MetricRequirements


@dataclass(frozen=True, slots=True)
class BoundarySpectralEntropyMetric:
    """Normalized entropy of eligible one-sided boundary power."""

    detrend: Detrend = "mean"
    id = "boundary_spectral_entropy"
    version = "1"
    requirements = MetricRequirements(min_stream_length=2)

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return detrending and normalization conventions."""
        return {"detrend": self.detrend, "normalized": True, "window": "rectangular"}

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None:
        """Require a matching stream with at least one gap."""
        validate_requirements(self.requirements, stream, boundaries)

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult:
        """Compute normalized entropy in [0, 1]."""
        self.validate_input(stream, boundaries)
        value = (
            BoundarySpectrumAnalysis(detrend=self.detrend)
            .compute(stream, boundaries)
            .spectral_entropy
        )
        return ScalarMetricResult(self.id, self.version, value, "normalized bits")
