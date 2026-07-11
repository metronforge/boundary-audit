"""Uniform segment-length permutation null model."""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.null_models.base import (
    BoundaryInvariant,
    NullModelCapabilities,
)


@dataclass(frozen=True, slots=True)
class LengthPermutationNullModel:
    """Uniformly permute the complete observed segment-length sequence."""

    id = "length_permutation"
    version = "1"
    capabilities = NullModelCapabilities(
        frozenset(
            {
                BoundaryInvariant.BOUNDARY_COUNT,
                BoundaryInvariant.SEGMENT_COUNT,
                BoundaryInvariant.SEGMENT_LENGTH_MULTISET,
            }
        )
    )

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return the empty parameter mapping."""
        return {}

    def sample(
        self,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        rng: np.random.Generator,
    ) -> BoundaryConfiguration:
        """Draw one independent permutation using the supplied RNG."""
        if len(stream) != observed.stream_length:
            from boundary_audit.core.errors import InvalidBoundaryConfigurationError

            raise InvalidBoundaryConfigurationError(
                "stream and configuration lengths differ"
            )
        lengths = np.asarray(observed.segment_lengths(), dtype=np.int64)
        return BoundaryConfiguration.from_segment_lengths(
            tuple(int(value) for value in rng.permutation(lengths))
        )
