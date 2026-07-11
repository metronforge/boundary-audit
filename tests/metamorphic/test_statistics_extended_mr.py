from dataclasses import dataclass

import numpy as np
import pytest

from boundary_audit import (
    BoundaryConfiguration,
    CompressionRatioMetric,
    NullModelComparison,
    NullModelError,
    SymbolStream,
)
from boundary_audit.core.types import JSONValue
from boundary_audit.null_models.base import NullModelCapabilities


@dataclass
class CountingNull:
    calls: int = 0
    id = "counting"
    version = "1"
    capabilities = NullModelCapabilities(frozenset())

    def parameters(self) -> dict[str, JSONValue]:
        return {}

    def sample(
        self,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        rng: np.random.Generator,
    ) -> BoundaryConfiguration:
        self.calls += 1
        return observed


def test_mr_stat_008_incompatible_capabilities_fail_before_sampling() -> None:
    stream = SymbolStream.from_text("abcd")
    model = CountingNull()
    with pytest.raises(NullModelError):
        NullModelComparison.run(
            stream=stream,
            observed=BoundaryConfiguration((2,), 4),
            metric=CompressionRatioMetric(),
            null_model=model,
            symbolization_id="char-v1",
            n_samples=2,
            seed=1,
        )
    assert model.calls == 0
