import numpy as np
import pytest

from boundary_audit import (
    BoundaryConfiguration,
    CompressionRatioMetric,
    EmpiricalRenewalNullModel,
    InvalidBoundaryConfigurationError,
    InvalidRegionError,
    InvalidSymbolError,
    MetricInputError,
    NullModelComparison,
    NullModelError,
    Region,
    SegmentLengthVarianceMetric,
    SymbolStream,
)
from boundary_audit.core.regions import validate_regions
from boundary_audit.core.types import JSONValue


def test_invalid_symbols_and_spaced_text_contract() -> None:
    with pytest.raises(InvalidSymbolError):
        SymbolStream.from_symbols([""])
    with pytest.raises(InvalidSymbolError):
        SymbolStream.from_spaced_text("a  b")


def test_unsorted_duplicate_and_out_of_range_contract() -> None:
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration((2, 1), 3)
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration((1, 1), 3)
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration((3,), 3)


def test_invalid_region_contract() -> None:
    with pytest.raises(InvalidRegionError):
        Region("x", 2, 2)
    with pytest.raises(InvalidRegionError):
        validate_regions((Region("a", 0, 3), Region("b", 2, 4)))


def test_insufficient_samples_and_capability_contract() -> None:
    stream = SymbolStream.from_text("abcd")
    observed = BoundaryConfiguration((2,), 4)
    with pytest.raises(MetricInputError):
        NullModelComparison.run(
            stream=stream,
            observed=observed,
            metric=SegmentLengthVarianceMetric(),
            null_model=EmpiricalRenewalNullModel(),
            symbolization_id="x",
            n_samples=1,
            seed=1,
        )
    with pytest.raises(NullModelError):
        NullModelComparison.run(
            stream=stream,
            observed=observed,
            metric=CompressionRatioMetric(),
            null_model=EmpiricalRenewalNullModel(),
            symbolization_id="x",
            n_samples=2,
            seed=1,
        )


def test_capability_failure_occurs_before_sampling_contract() -> None:
    class CountingRenewal:
        id = "counting_renewal"
        version = "1"
        capabilities = EmpiricalRenewalNullModel.capabilities

        def __init__(self) -> None:
            self.calls = 0

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

    model = CountingRenewal()
    stream = SymbolStream.from_text("abcd")
    with pytest.raises(NullModelError):
        NullModelComparison.run(
            stream=stream,
            observed=BoundaryConfiguration((2,), 4),
            metric=CompressionRatioMetric(),
            null_model=model,
            symbolization_id="x",
            n_samples=2,
            seed=1,
        )
    assert model.calls == 0
