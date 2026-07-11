from hypothesis import given
from hypothesis import strategies as st

from boundary_audit import BoundaryConfiguration, SymbolStream


@st.composite
def stream_and_boundaries(
    draw: st.DrawFn,
) -> tuple[SymbolStream, BoundaryConfiguration]:
    symbols = draw(st.lists(st.sampled_from(["a", "b", "qo"]), min_size=1, max_size=20))
    stream = SymbolStream.from_symbols(symbols)
    positions = draw(
        st.lists(
            st.integers(min_value=1, max_value=max(1, len(stream) - 1)),
            unique=True,
            max_size=max(0, len(stream) - 1),
        )
    )
    valid = tuple(sorted(position for position in positions if position < len(stream)))
    return stream, BoundaryConfiguration(valid, len(stream))


@given(stream_and_boundaries())
def test_mr_core_001_segment_rejoin_reconstructs_stream(
    case: tuple[SymbolStream, BoundaryConfiguration],
) -> None:
    stream, boundaries = case
    assert (
        tuple(symbol for segment in boundaries.segments(stream) for symbol in segment)
        == stream.symbols
    )


@given(stream_and_boundaries())
def test_mr_core_002_positions_lengths_round_trip(
    case: tuple[SymbolStream, BoundaryConfiguration],
) -> None:
    _, boundaries = case
    assert (
        BoundaryConfiguration.from_segment_lengths(boundaries.segment_lengths())
        == boundaries
    )


@given(stream_and_boundaries())
def test_mr_core_003_positions_indicator_round_trip(
    case: tuple[SymbolStream, BoundaryConfiguration],
) -> None:
    _, boundaries = case
    assert BoundaryConfiguration.from_indicator(boundaries.to_indicator()) == boundaries


@given(stream_and_boundaries())
def test_mr_core_004_bijective_renaming_preserves_structure(
    case: tuple[SymbolStream, BoundaryConfiguration],
) -> None:
    stream, boundaries = case
    mapping = {
        symbol: f"renamed-{index}"
        for index, symbol in enumerate(stream.alphabet().symbols)
    }
    assert stream.rename(mapping).alphabet().size == stream.alphabet().size
    assert boundaries.segment_lengths() == boundaries.segment_lengths()


@given(stream_and_boundaries())
def test_mr_core_005_reverse_twice_is_identity(
    case: tuple[SymbolStream, BoundaryConfiguration],
) -> None:
    stream, boundaries = case
    assert stream.reverse().reverse() == stream
    assert boundaries.reverse().reverse() == boundaries


@given(stream_and_boundaries())
def test_mr_core_006_mirrored_boundaries(
    case: tuple[SymbolStream, BoundaryConfiguration],
) -> None:
    _, boundaries = case
    assert boundaries.reverse().positions == tuple(
        sorted(boundaries.stream_length - p for p in boundaries.positions)
    )
