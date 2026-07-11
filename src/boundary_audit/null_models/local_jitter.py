"""Joint-rejection local boundary jitter."""

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import NullModelError, NullModelSamplingError
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.null_models.base import COUNT_CAPABILITIES


@dataclass(frozen=True, slots=True)
class LocalJitterNullModel:
    """Shift all positions jointly and reject the complete invalid proposal."""

    max_shift: int
    max_retries: int = 100
    id = "local_jitter"
    version = "1"
    capabilities = COUNT_CAPABILITIES

    def __post_init__(self) -> None:
        if self.max_shift < 0:
            raise NullModelError("max_shift must be non-negative")
        if self.max_retries < 1:
            raise NullModelError("max_retries must be at least 1")

    def parameters(self) -> Mapping[str, JSONValue]:
        """Return jitter parameters."""
        return {"max_shift": self.max_shift, "max_retries": self.max_retries}

    def sample(
        self,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        rng: np.random.Generator,
    ) -> BoundaryConfiguration:
        """Return the first valid joint proposal."""
        if len(stream) != observed.stream_length:
            raise NullModelError("stream and configuration lengths differ")
        if self.max_shift == 0 or observed.count == 0:
            return observed
        base = np.asarray(observed.positions, dtype=np.int64)
        for _ in range(self.max_retries):
            shifts = rng.integers(
                -self.max_shift, self.max_shift + 1, size=observed.count
            )
            candidate = tuple(int(value) for value in base + shifts)
            if all(1 <= value < len(stream) for value in candidate) and all(
                a < b for a, b in zip(candidate, candidate[1:], strict=False)
            ):
                return BoundaryConfiguration(candidate, len(stream))
        raise NullModelSamplingError(
            f"local jitter exhausted {self.max_retries} joint proposals"
        )
