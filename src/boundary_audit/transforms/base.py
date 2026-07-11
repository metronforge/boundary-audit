"""Deterministic boundary-transform protocol."""

from typing import Protocol

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.stream import SymbolStream


class BoundaryTransform(Protocol):
    """A deterministic transform, deliberately distinct from a null model."""

    id: str
    version: str

    def apply(
        self, stream: SymbolStream, observed: BoundaryConfiguration
    ) -> BoundaryConfiguration:
        """Transform one matching configuration."""
        ...
