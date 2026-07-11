import numpy as np
from hypothesis import given
from hypothesis import strategies as st

from boundary_audit import (
    BoundaryConfiguration,
    EmpiricalRenewalNullModel,
    FixedCountUniformNullModel,
    LengthPermutationNullModel,
    LocalJitterNullModel,
    SymbolStream,
)


@given(st.integers(2, 30), st.integers(0, 2**32 - 1))
def test_mr_null_001_fixed_count_preserves_count(n: int, seed: int) -> None:
    stream = SymbolStream.from_symbols([str(i % 3) for i in range(n)])
    observed = BoundaryConfiguration(tuple(range(2, n, 3)), n)
    sampled = FixedCountUniformNullModel().sample(
        stream, observed, np.random.default_rng(seed)
    )
    assert sampled.count == observed.count


@given(st.lists(st.integers(1, 8), min_size=1, max_size=10), st.integers(0, 2**32 - 1))
def test_mr_null_002_length_permutation_preserves_multiset(
    lengths: list[int], seed: int
) -> None:
    observed = BoundaryConfiguration.from_segment_lengths(lengths)
    stream = SymbolStream.from_symbols(["x"] * observed.stream_length)
    sampled = LengthPermutationNullModel().sample(
        stream, observed, np.random.default_rng(seed)
    )
    assert sorted(sampled.segment_lengths()) == sorted(lengths)


@given(st.integers(1, 30))
def test_mr_null_003_zero_jitter_identity(n: int) -> None:
    stream = SymbolStream.from_symbols(["x"] * n)
    observed = BoundaryConfiguration(tuple(range(1, n)), n)
    assert (
        LocalJitterNullModel(0).sample(stream, observed, np.random.default_rng(1))
        == observed
    )


@given(st.integers(1, 30), st.integers(0, 2**32 - 1))
def test_mr_null_004_all_samples_are_valid(n: int, seed: int) -> None:
    stream = SymbolStream.from_symbols(["x"] * n)
    observed = BoundaryConfiguration(tuple(range(2, n, 4)), n)
    sample = EmpiricalRenewalNullModel().sample(
        stream, observed, np.random.default_rng(seed)
    )
    assert sum(sample.segment_lengths()) == n
    assert all(length > 0 for length in sample.segment_lengths())


@given(st.integers(2, 30), st.integers(0, 2**32 - 1), st.integers(0, 30))
def test_mr_null_005_spawn_key_reproduces_candidate(
    n: int, seed: int, slot: int
) -> None:
    stream = SymbolStream.from_symbols(["x"] * n)
    observed = BoundaryConfiguration(tuple(range(2, n, 3)), n)
    model = FixedCountUniformNullModel()

    def draw() -> BoundaryConfiguration:
        rng = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(slot, 0)))
        return model.sample(stream, observed, rng)

    assert draw() == draw()


@given(st.integers(2, 30), st.integers(0, 2**32 - 1))
def test_mr_null_006_symbol_renaming_preserves_sampled_positions(
    n: int, seed: int
) -> None:
    stream = SymbolStream.from_symbols([str(i % 2) for i in range(n)])
    renamed = stream.rename({"0": "a", "1": "b"})
    observed = BoundaryConfiguration(tuple(range(2, n, 3)), n)
    model = FixedCountUniformNullModel()
    assert model.sample(stream, observed, np.random.default_rng(seed)) == model.sample(
        renamed, observed, np.random.default_rng(seed)
    )
