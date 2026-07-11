"""Conditioned empirical-renewal approximation."""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import InvalidBoundaryConfigurationError
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.null_models.base import NullModelCapabilities


@dataclass(frozen=True, slots=True)
class EmpiricalRenewalNullModel:
    """Sample empirical lengths, adjusting the final segment to avoid overshoot."""

    id = "empirical_renewal"
    version = "1"
    capabilities = NullModelCapabilities(frozenset())

    def parameters(self) -> Mapping[str, JSONValue]:
        """Describe the conditioned-renewal algorithm."""
        return {"conditioned_to_stream_length": True}

    def sample(
        self,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        rng: np.random.Generator,
    ) -> BoundaryConfiguration:
        """Generate positive segments summing exactly to the stream length."""
        if len(stream) != observed.stream_length:
            raise InvalidBoundaryConfigurationError(
                "stream and configuration lengths differ"
            )
        empirical = observed.segment_lengths()
        remaining = len(stream)
        lengths: list[int] = []
        while remaining:
            draw = int(rng.choice(empirical))
            if draw >= remaining:
                lengths.append(remaining)
                remaining = 0
            else:
                lengths.append(draw)
                remaining -= draw
        return BoundaryConfiguration.from_segment_lengths(lengths)
