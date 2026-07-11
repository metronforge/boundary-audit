"""Immutable boundary configurations and exact round trips."""

from collections.abc import Iterable
from dataclasses import dataclass

from boundary_audit.core.errors import (
    BoundaryOutOfRangeError,
    InvalidBoundaryConfigurationError,
)
from boundary_audit.core.stream import SymbolStream


@dataclass(frozen=True, slots=True)
class BoundaryConfiguration:
    """Strictly increasing internal split positions for one stream length."""

    positions: tuple[int, ...]
    stream_length: int

    def __post_init__(self) -> None:
        if self.stream_length < 1:
            raise InvalidBoundaryConfigurationError("stream_length must be at least 1")
        if any(
            not isinstance(position, int) or isinstance(position, bool)
            for position in self.positions
        ):
            raise InvalidBoundaryConfigurationError(
                "boundary positions must be integers"
            )
        if any(
            a >= b for a, b in zip(self.positions, self.positions[1:], strict=False)
        ):
            raise InvalidBoundaryConfigurationError(
                "boundary positions must already be strictly increasing"
            )
        if any(
            position < 1 or position >= self.stream_length
            for position in self.positions
        ):
            raise BoundaryOutOfRangeError(
                f"boundaries must lie in 1..{self.stream_length - 1}"
            )

    @classmethod
    def from_positions(
        cls, positions: Iterable[int], *, stream_length: int, normalize: bool = False
    ) -> "BoundaryConfiguration":
        """Construct, optionally making sorting/deduplication explicit."""
        values = tuple(positions)
        if normalize:
            values = tuple(sorted(set(values)))
        return cls(values, stream_length)

    @classmethod
    def from_indicator(cls, indicator: Iterable[int]) -> "BoundaryConfiguration":
        """Reconstruct positions from a binary gap indicator."""
        values = tuple(indicator)
        if any(value not in (0, 1) for value in values):
            raise InvalidBoundaryConfigurationError("indicator values must be 0 or 1")
        return cls(
            tuple(i + 1 for i, value in enumerate(values) if value), len(values) + 1
        )

    @classmethod
    def from_segment_lengths(cls, lengths: Iterable[int]) -> "BoundaryConfiguration":
        """Reconstruct positions from positive segment lengths."""
        values = tuple(lengths)
        if not values or any(
            not isinstance(value, int) or value <= 0 for value in values
        ):
            raise InvalidBoundaryConfigurationError(
                "segment lengths must be positive integers"
            )
        positions: list[int] = []
        cursor = 0
        for length in values[:-1]:
            cursor += length
            positions.append(cursor)
        return cls(tuple(positions), sum(values))

    @property
    def count(self) -> int:
        """Return the number of explicit boundaries."""
        return len(self.positions)

    @property
    def segment_count(self) -> int:
        """Return the implied segment count."""
        return self.count + 1

    def to_indicator(self) -> tuple[int, ...]:
        """Return a binary value for every adjacent symbol gap."""
        present = set(self.positions)
        return tuple(
            int(position in present) for position in range(1, self.stream_length)
        )

    def segment_lengths(self) -> tuple[int, ...]:
        """Return exact positive segment lengths."""
        endpoints = (0, *self.positions, self.stream_length)
        return tuple(b - a for a, b in zip(endpoints, endpoints[1:], strict=False))

    def segments(self, stream: SymbolStream) -> tuple[tuple[str, ...], ...]:
        """Split a matching stream into exact symbol tuples."""
        if len(stream) != self.stream_length:
            raise InvalidBoundaryConfigurationError(
                "stream and configuration lengths differ"
            )
        endpoints = (0, *self.positions, self.stream_length)
        return tuple(
            stream.symbols[a:b] for a, b in zip(endpoints, endpoints[1:], strict=False)
        )

    def reverse(self) -> "BoundaryConfiguration":
        """Mirror every split position around the stream midpoint."""
        return BoundaryConfiguration(
            tuple(sorted(self.stream_length - position for position in self.positions)),
            self.stream_length,
        )
