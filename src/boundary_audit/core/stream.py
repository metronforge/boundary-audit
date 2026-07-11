"""Immutable symbolic streams."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from boundary_audit.core.alphabet import Alphabet
from boundary_audit.core.errors import EmptyStreamError, InvalidSymbolError

if TYPE_CHECKING:
    from boundary_audit.core.boundaries import BoundaryConfiguration


@dataclass(frozen=True, slots=True)
class SymbolStream:
    """A finite non-empty sequence of caller-supplied atomic strings."""

    symbols: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.symbols:
            raise EmptyStreamError("a symbol stream must contain at least one symbol")
        if any(not isinstance(symbol, str) or not symbol for symbol in self.symbols):
            raise InvalidSymbolError("every symbol must be a non-empty Python str")

    @classmethod
    def from_symbols(cls, symbols: Iterable[str]) -> "SymbolStream":
        """Construct from explicit atomic symbols."""
        return cls(tuple(symbols))

    @classmethod
    def from_text(cls, text: str) -> "SymbolStream":
        """Construct by splitting text into Python Unicode code points."""
        return cls(tuple(text))

    @classmethod
    def from_spaced_text(
        cls, text: str, separator: str = " "
    ) -> tuple["SymbolStream", "BoundaryConfiguration"]:
        """Parse separated character-level segments under the v0.1 convention."""
        from boundary_audit.core.boundaries import BoundaryConfiguration

        if not separator:
            raise InvalidSymbolError("separator must be a non-empty string")
        if text.startswith(separator) or text.endswith(separator):
            raise InvalidSymbolError("leading and trailing separators are invalid")
        parts = text.split(separator)
        if any(not part for part in parts):
            raise InvalidSymbolError(
                "repeated separators and empty segments are invalid"
            )
        symbols = tuple(symbol for part in parts for symbol in part)
        stream = cls(symbols)
        positions: list[int] = []
        offset = 0
        for part in parts[:-1]:
            offset += len(part)
            positions.append(offset)
        return stream, BoundaryConfiguration(tuple(positions), len(stream))

    def __len__(self) -> int:
        return len(self.symbols)

    def __str__(self) -> str:
        return self.to_text()

    def to_symbols(self) -> tuple[str, ...]:
        """Return exact atomic symbols."""
        return self.symbols

    def to_text(self, separator: str = "") -> str:
        """Return a non-canonical display string."""
        return separator.join(self.symbols)

    def alphabet(self) -> Alphabet:
        """Return the deterministic first-observed alphabet."""
        return Alphabet.from_symbols(self.symbols)

    def reverse(self) -> "SymbolStream":
        """Return the reversed symbol stream."""
        return SymbolStream(tuple(reversed(self.symbols)))

    def rename(self, mapping: Mapping[str, str]) -> "SymbolStream":
        """Apply a bijection over the observed alphabet."""
        observed = set(self.alphabet().symbols)
        if set(mapping) != observed:
            raise InvalidSymbolError(
                "rename mapping must cover the observed alphabet exactly"
            )
        values = tuple(mapping[symbol] for symbol in self.alphabet().symbols)
        if any(not isinstance(value, str) or not value for value in values):
            raise InvalidSymbolError("renamed symbols must be non-empty strings")
        if len(set(values)) != len(values):
            raise InvalidSymbolError("rename mapping must be bijective")
        return SymbolStream(tuple(mapping[symbol] for symbol in self.symbols))
