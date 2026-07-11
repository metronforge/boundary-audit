from collections import Counter

from hypothesis import given
from hypothesis import strategies as st

from boundary_audit import (
    BlockComplexityAnalysis,
    BoundaryConfiguration,
    ConditionalEntropyAnalysis,
    NGramAnalysis,
    SymbolStream,
    TransitionAnalysis,
)


@given(st.lists(st.sampled_from(["a", "b", "c"]), min_size=3, max_size=20))
def test_mr_dyn_001_full_equals_within_plus_across(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    boundaries = BoundaryConfiguration(tuple(range(2, len(stream), 3)), len(stream))
    full = Counter(NGramAnalysis(2, "full").compute(stream, boundaries).counts)
    partition = Counter(NGramAnalysis(2, "within").compute(stream, boundaries).counts)
    partition.update(NGramAnalysis(2, "across").compute(stream, boundaries).counts)
    assert full == partition


@given(st.lists(st.sampled_from(["a", "b"]), min_size=2, max_size=20))
def test_mr_dyn_002_renaming_preserves_block_complexity(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    renamed = stream.rename(
        {s: f"x-{i}" for i, s in enumerate(stream.alphabet().symbols)}
    )
    boundaries = BoundaryConfiguration((), len(stream))
    assert (
        BlockComplexityAnalysis(2).compute(stream, boundaries).value
        == BlockComplexityAnalysis(2).compute(renamed, boundaries).value
    )


@given(st.lists(st.sampled_from(["a", "b", "c"]), min_size=2, max_size=20))
def test_mr_dyn_003_reversal_reverses_ngrams(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    boundaries = BoundaryConfiguration((), len(stream))
    source = NGramAnalysis(2).compute(stream, boundaries).counts
    reversed_counts = NGramAnalysis(2).compute(stream.reverse(), boundaries).counts
    assert {tuple(reversed(k)): v for k, v in source.items()} == reversed_counts


@given(st.integers(11, 30))
def test_mr_dyn_004_constant_stream_conditional_entropy_zero(n: int) -> None:
    stream = SymbolStream.from_symbols(["x"] * n)
    boundaries = BoundaryConfiguration((), n)
    assert (
        ConditionalEntropyAnalysis(min_observations=10)
        .compute(stream, boundaries)
        .entropy_bits
        == 0.0
    )


@given(st.lists(st.sampled_from(["a", "b"]), min_size=2, max_size=20))
def test_mr_dyn_005_transition_totals_equal_windows(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    result = TransitionAnalysis().compute(
        stream, BoundaryConfiguration((), len(stream))
    )
    assert (
        sum(sum(row.values()) for row in result.counts.values()) == result.sample_count
    )
