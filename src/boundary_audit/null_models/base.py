"""Null-model protocols and declarative capabilities."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue


class BoundaryInvariant(StrEnum):
    """Properties guaranteed for every successful null sample."""

    BOUNDARY_COUNT = "boundary_count"
    SEGMENT_COUNT = "segment_count"
    SEGMENT_LENGTH_MULTISET = "segment_length_multiset"
    PER_REGION_BOUNDARY_COUNT = "per_region_boundary_count"
    OUTSIDE_REGION_BOUNDARIES = "outside_region_boundaries"


@dataclass(frozen=True, slots=True)
class NullModelCapabilities:
    """Declarative invariants guaranteed by a null model."""

    guaranteed_invariants: frozenset[BoundaryInvariant]


class BoundaryNullModel(Protocol):
    """A probability law over boundary configurations."""

    id: str
    version: str
    capabilities: NullModelCapabilities

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return deterministic JSON-compatible algorithm parameters."""
        ...

    def sample(
        self,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        rng: np.random.Generator,
    ) -> BoundaryConfiguration:
        """Draw one candidate using only the supplied RNG."""
        ...


COUNT_CAPABILITIES = NullModelCapabilities(
    frozenset({BoundaryInvariant.BOUNDARY_COUNT, BoundaryInvariant.SEGMENT_COUNT})
)
