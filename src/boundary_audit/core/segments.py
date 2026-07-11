"""Segment helper functions."""

from collections.abc import Iterable

from boundary_audit.core.boundaries import BoundaryConfiguration


def boundaries_from_segment_lengths(lengths: Iterable[int]) -> BoundaryConfiguration:
    """Return the boundary configuration implied by positive lengths."""
    return BoundaryConfiguration.from_segment_lengths(lengths)
