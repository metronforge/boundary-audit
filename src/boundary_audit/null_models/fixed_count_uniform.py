"""Uniform fixed-boundary-count null model."""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import InvalidBoundaryConfigurationError
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.null_models.base import COUNT_CAPABILITIES


@dataclass(frozen=True, slots=True)
class FixedCountUniformNullModel:
    """Uniformly draw a fixed-size subset of all internal gaps."""

    id = "fixed_count_uniform"
    version = "1"
    capabilities = COUNT_CAPABILITIES

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return the empty parameter mapping."""
        return {}

    def sample(
        self,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        rng: np.random.Generator,
    ) -> BoundaryConfiguration:
        """Draw without replacement within this configuration."""
        if len(stream) != observed.stream_length:
            raise InvalidBoundaryConfigurationError(
                "stream and configuration lengths differ"
            )
        if observed.count == 0:
            return BoundaryConfiguration((), len(stream))
        selected = rng.choice(
            np.arange(1, len(stream), dtype=np.int64),
            size=observed.count,
            replace=False,
        )
        return BoundaryConfiguration(
            tuple(sorted(int(value) for value in selected)), len(stream)
        )
