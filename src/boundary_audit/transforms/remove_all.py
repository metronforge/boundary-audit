"""Boundary removal transform."""

from dataclasses import dataclass

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import InvalidBoundaryConfigurationError
from boundary_audit.core.stream import SymbolStream


@dataclass(frozen=True, slots=True)
class RemoveAllBoundaries:
    """Remove every supplied boundary deterministically."""

    id = "remove_all_boundaries"
    version = "1"

    def apply(
        self, stream: SymbolStream, observed: BoundaryConfiguration
    ) -> BoundaryConfiguration:
        """Return an empty configuration for the matching stream."""
        if len(stream) != observed.stream_length:
            raise InvalidBoundaryConfigurationError(
                "stream and configuration lengths differ"
            )
        return BoundaryConfiguration((), len(stream))
