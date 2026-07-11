"""Half-open regions used by blockwise null models."""

from collections.abc import Sequence
from dataclasses import dataclass

from boundary_audit.core.errors import InvalidRegionError


@dataclass(frozen=True, slots=True)
class Region:
    """A named half-open interval ``[start, end)``."""

    name: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidRegionError("region name must be non-empty")
        if self.start < 0 or self.end <= self.start:
            raise InvalidRegionError("region must satisfy 0 <= start < end")

    def validate_for_stream(self, stream_length: int) -> None:
        """Validate the region's upper bound for a specific stream."""
        if self.end > stream_length:
            raise InvalidRegionError("region end exceeds stream length")

    def contains_internal(self, position: int) -> bool:
        """Return whether a boundary is strictly internal to this region."""
        return self.start < position < self.end


def validate_regions(
    regions: Sequence[Region], stream_length: int | None = None
) -> None:
    """Validate sorted, non-overlapping regions; adjacency is allowed."""
    for previous, current in zip(regions, regions[1:], strict=False):
        if previous.start > current.start or previous.end > current.start:
            raise InvalidRegionError("regions must be sorted and non-overlapping")
    if stream_length is not None:
        for region in regions:
            region.validate_for_stream(stream_length)
