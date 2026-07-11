"""Deterministic observed alphabet."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Alphabet:
    """Symbols in first-observed order."""

    symbols: tuple[str, ...]

    @classmethod
    def from_symbols(cls, symbols: tuple[str, ...]) -> "Alphabet":
        """Build an alphabet without hash-order dependence."""
        return cls(tuple(dict.fromkeys(symbols)))

    @property
    def size(self) -> int:
        """Return the number of distinct symbols."""
        return len(self.symbols)

    def sorted_symbols(self) -> tuple[str, ...]:
        """Return an explicit lexicographically sorted view."""
        return tuple(sorted(self.symbols))
