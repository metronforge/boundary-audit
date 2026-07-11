import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from boundary_audit import (
    BlockwiseFixedCountNullModel,
    BoundaryConfiguration,
    BoundaryInvariant,
    FixedCountUniformNullModel,
    Region,
    SegmentLengthVarianceMetric,
    SymbolStream,
)
from boundary_audit.statistics.null_distribution import (
    NullDistribution,
    evaluate_slot,
    generate_null_distribution,
)


@given(st.integers(4, 30), st.integers(0, 2**32 - 1))
def test_mr_null_007_permuted_slot_evaluation_preserves_order(
    n: int, seed: int
) -> None:
    stream = SymbolStream.from_symbols(["x"] * n)
    observed = BoundaryConfiguration(tuple(range(2, n, 4)), n)
    model = FixedCountUniformNullModel()
    metric = SegmentLengthVarianceMetric()
    source = [
        evaluate_slot(
            slot=i,
            master_seed=seed,
            max_attempts=3,
            stream=stream,
            observed=observed,
            metric=metric,
            null_model=model,
        )
        for i in range(6)
    ]
    follow = [
        evaluate_slot(
            slot=i,
            master_seed=seed,
            max_attempts=3,
            stream=stream,
            observed=observed,
            metric=metric,
            null_model=model,
        )
        for i in reversed(range(6))
    ]
    assert [result.value for result in source] == [
        result.value for result in reversed(follow)
    ]


def test_mr_null_008_parallel_slots_are_retry_independent() -> None:
    stream = SymbolStream.from_text("abcdefghijkl")
    observed = BoundaryConfiguration((3, 6, 9), 12)

    def generate(workers: int) -> NullDistribution:
        return generate_null_distribution(
            stream=stream,
            observed=observed,
            metric=SegmentLengthVarianceMetric(),
            null_model=FixedCountUniformNullModel(),
            master_seed=7,
            n_samples=10,
            max_attempts=4,
            workers=workers,
        )

    assert generate(1) == generate(4)


@given(st.integers(6, 20), st.integers(0, 2**32 - 1))
def test_mr_null_009_declared_blockwise_capabilities_hold(n: int, seed: int) -> None:
    stream = SymbolStream.from_symbols(["x"] * n)
    observed = BoundaryConfiguration((1, 2, n - 2, n - 1), n)
    model = BlockwiseFixedCountNullModel((Region("middle", 1, n - 1),))
    sampled = model.sample(stream, observed, np.random.default_rng(seed))
    assert sampled.count == observed.count
    assert {p for p in sampled.positions if p <= 1 or p >= n - 1} == {1, n - 1}
    assert (
        BoundaryInvariant.PER_REGION_BOUNDARY_COUNT
        in model.capabilities.guaranteed_invariants
    )
