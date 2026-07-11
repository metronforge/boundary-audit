"""Canonical structural compression metric and analysis."""

import zlib
from collections.abc import Mapping
from dataclasses import dataclass

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.serialization import (
    SERIALIZATION_VERSION,
    structural_stream_bytes,
)
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.metrics.base import ScalarMetricResult, validate_requirements
from boundary_audit.metrics.requirements import MetricRequirements
from boundary_audit.null_models.base import BoundaryInvariant


@dataclass(frozen=True, slots=True)
class CompressionResult:
    """Sizes and ratio for the canonical structural payload."""

    compressed_bytes: int
    uncompressed_bytes: int
    ratio: float
    boundary_count: int
    serialization_version: int


def compression_result(
    stream: SymbolStream, boundaries: BoundaryConfiguration
) -> CompressionResult:
    """Compress canonical ID/boundary framing using zlib."""
    payload = structural_stream_bytes(stream, boundaries)
    compressed = zlib.compress(payload)
    return CompressionResult(
        len(compressed),
        len(payload),
        len(compressed) / len(payload),
        boundaries.count,
        SERIALIZATION_VERSION,
    )


@dataclass(frozen=True, slots=True)
class CompressionRatioMetric:
    """Compressed-to-uncompressed canonical structural byte ratio."""

    id = "compression_ratio"
    version = "1"
    requirements = MetricRequirements(
        required_null_invariants=frozenset({BoundaryInvariant.BOUNDARY_COUNT})
    )

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return compression and serialization conventions."""
        return {"algorithm": "zlib", "serialization_version": SERIALIZATION_VERSION}

    def validate_input(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> None:
        """Validate common preconditions."""
        validate_requirements(self.requirements, stream, boundaries)

    def compute(
        self, stream: SymbolStream, boundaries: BoundaryConfiguration
    ) -> ScalarMetricResult:
        """Compute compressed size divided by uncompressed size."""
        self.validate_input(stream, boundaries)
        return ScalarMetricResult(
            self.id, self.version, compression_result(stream, boundaries).ratio, "ratio"
        )
