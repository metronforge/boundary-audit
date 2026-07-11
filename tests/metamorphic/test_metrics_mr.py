import pytest
from hypothesis import given
from hypothesis import strategies as st

from boundary_audit import (
    BoundaryConfiguration,
    BoundaryPairMutualInformationMetric,
    CompressionRatioMetric,
    PositionalEntropyDifferenceMetric,
    SegmentLengthEntropyMetric,
    SegmentLengthVarianceMetric,
    SymbolStream,
    compression_result,
    positional_entropies,
)
from boundary_audit.core.serialization import exact_stream_bytes


@given(st.lists(st.sampled_from(["a", "b"]), min_size=2, max_size=20))
def test_mr_met_001_boundary_mi_renaming_invariant(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    renamed = stream.rename(
        {s: f"r-{i}" for i, s in enumerate(stream.alphabet().symbols)}
    )
    boundaries = BoundaryConfiguration(tuple(range(2, len(stream), 3)), len(stream))
    metric = BoundaryPairMutualInformationMetric()
    assert metric.compute(stream, boundaries).value == pytest.approx(
        metric.compute(renamed, boundaries).value
    )


@given(st.lists(st.sampled_from(["a", "b", "c"]), min_size=2, max_size=20))
def test_mr_met_002_boundary_mi_reversal_invariant(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    boundaries = BoundaryConfiguration(tuple(range(2, len(stream), 3)), len(stream))
    metric = BoundaryPairMutualInformationMetric()
    assert metric.compute(stream, boundaries).value == pytest.approx(
        metric.compute(stream.reverse(), boundaries.reverse()).value
    )


@given(st.lists(st.sampled_from(["a", "b", "c"]), min_size=2, max_size=20))
def test_mr_met_003_positional_entropies_swap_on_reverse(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    boundaries = BoundaryConfiguration(tuple(range(1, len(stream))), len(stream))
    source = positional_entropies(stream, boundaries)
    follow = positional_entropies(stream.reverse(), boundaries.reverse())
    assert source.initial_entropy == pytest.approx(follow.final_entropy)
    assert source.final_entropy == pytest.approx(follow.initial_entropy)


@given(st.lists(st.integers(1, 8), min_size=2, max_size=10))
def test_mr_met_004_005_segment_metrics_mirror_invariant(lengths: list[int]) -> None:
    boundaries = BoundaryConfiguration.from_segment_lengths(lengths)
    stream = SymbolStream.from_symbols(["x"] * boundaries.stream_length)
    for metric in (
        SegmentLengthEntropyMetric(),
        SegmentLengthVarianceMetric(),
        PositionalEntropyDifferenceMetric(),
    ):
        assert metric.compute(stream, boundaries).value == pytest.approx(
            metric.compute(stream.reverse(), boundaries.reverse()).value
        )


@given(st.lists(st.sampled_from(["a", "b"]), min_size=1, max_size=20))
def test_mr_met_006_compression_renaming_invariant(symbols: list[str]) -> None:
    stream = SymbolStream.from_symbols(symbols)
    renamed = stream.rename(
        {s: f"long-{i}" for i, s in enumerate(stream.alphabet().symbols)}
    )
    boundaries = BoundaryConfiguration(tuple(range(2, len(stream), 3)), len(stream))
    assert (
        CompressionRatioMetric().compute(stream, boundaries).value
        == CompressionRatioMetric().compute(renamed, boundaries).value
    )
    assert (
        compression_result(stream, boundaries).compressed_bytes
        == compression_result(renamed, boundaries).compressed_bytes
    )


def test_mr_met_007_exact_framing_distinguishes_ambiguous_text() -> None:
    assert exact_stream_bytes(
        SymbolStream.from_symbols(["qo", "k"])
    ) != exact_stream_bytes(SymbolStream.from_symbols(["q", "ok"]))
