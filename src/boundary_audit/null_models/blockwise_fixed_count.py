"""Region-wise fixed-count uniform null model."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import NullModelError
from boundary_audit.core.regions import Region, validate_regions
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.null_models.base import BoundaryInvariant, NullModelCapabilities


@dataclass(frozen=True, slots=True)
class BlockwiseFixedCountNullModel:
    """Preserve internal counts by region and all boundaries outside regions."""

    regions: tuple[Region, ...]
    id = "blockwise_fixed_count"
    version = "1"
    capabilities = NullModelCapabilities(
        frozenset(
            {
                BoundaryInvariant.BOUNDARY_COUNT,
                BoundaryInvariant.SEGMENT_COUNT,
                BoundaryInvariant.PER_REGION_BOUNDARY_COUNT,
                BoundaryInvariant.OUTSIDE_REGION_BOUNDARIES,
            }
        )
    )

    def __init__(self, regions: Sequence[Region]) -> None:
        values = tuple(regions)
        validate_regions(values)
        object.__setattr__(self, "regions", values)

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return canonical region definitions."""
        return {
            "regions": [
                {"name": region.name, "start": region.start, "end": region.end}
                for region in self.regions
            ]
        }

    def sample(
        self,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        rng: np.random.Generator,
    ) -> BoundaryConfiguration:
        """Sample each region independently with its observed internal count."""
        if len(stream) != observed.stream_length:
            raise NullModelError("stream and configuration lengths differ")
        validate_regions(self.regions, len(stream))
        covered = {
            position
            for region in self.regions
            for position in range(region.start + 1, region.end)
        }
        sampled = [
            position for position in observed.positions if position not in covered
        ]
        observed_set = set(observed.positions)
        for region in self.regions:
            eligible = np.arange(region.start + 1, region.end, dtype=np.int64)
            count = sum(position in observed_set for position in eligible)
            if count > len(eligible):
                raise NullModelError(f"impossible count in region {region.name!r}")
            if count:
                sampled.extend(
                    int(value) for value in rng.choice(eligible, count, replace=False)
                )
        return BoundaryConfiguration(tuple(sorted(sampled)), len(stream))
