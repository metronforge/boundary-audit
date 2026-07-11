import math

import numpy as np
import pytest

from boundary_audit import (
    AnalysisInputError,
    BlockComplexityAnalysis,
    BoundaryConfiguration,
    BoundaryOutOfRangeError,
    BoundarySpectralEntropyMetric,
    BoundarySpectrumAnalysis,
    EmptyStreamError,
    ForbiddenNGramAnalysis,
    ForbiddenNGramFractionMetric,
    InvalidBoundaryConfigurationError,
    InvalidRegionError,
    InvalidSymbolError,
    LocalJitterNullModel,
    MetricInputError,
    NGramAnalysis,
    NullModelError,
    Region,
    SegmentLengthSpectrumAnalysis,
    SerializationError,
    SymbolStream,
    TransitionAnalysis,
    autocorrelation,
)
from boundary_audit.core.serialization import (
    canonical_json_bytes,
    encode_uleb128,
    structural_stream_bytes,
)
from boundary_audit.metrics.base import ScalarMetricResult
from boundary_audit.statistics.multiple_testing import (
    benjamini_hochberg_adjust,
    holm_adjust,
)
from boundary_audit.statistics.pvalue import empirical_p_value


def test_stream_constructors_display_and_validation() -> None:
    stream, boundaries = SymbolStream.from_spaced_text("ab cd")
    assert stream.to_text("-") == "a-b-c-d"
    assert str(stream) == "abcd"
    assert stream.to_symbols() == ("a", "b", "c", "d")
    assert boundaries.positions == (2,)
    assert stream.alphabet().sorted_symbols() == ("a", "b", "c", "d")
    with pytest.raises(EmptyStreamError):
        SymbolStream.from_text("")
    with pytest.raises(InvalidSymbolError):
        SymbolStream.from_spaced_text(" ab")
    with pytest.raises(InvalidSymbolError):
        SymbolStream.from_spaced_text("ab ")
    with pytest.raises(InvalidSymbolError):
        SymbolStream.from_spaced_text("ab", "")
    with pytest.raises(InvalidSymbolError):
        stream.rename({"a": "x"})
    with pytest.raises(InvalidSymbolError):
        stream.rename({symbol: "x" for symbol in stream.alphabet().symbols})


def test_boundary_factories_and_validation_branches() -> None:
    assert BoundaryConfiguration.from_positions(
        [2, 1, 2], stream_length=3, normalize=True
    ).positions == (1, 2)
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration((True,), 2)
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration.from_indicator([0, 2])
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration.from_segment_lengths([])
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration.from_segment_lengths([1, 0])
    with pytest.raises(BoundaryOutOfRangeError):
        BoundaryConfiguration((0,), 2)
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration((1,), 0)
    with pytest.raises(InvalidBoundaryConfigurationError):
        BoundaryConfiguration((1,), 2).segments(SymbolStream.from_text("abc"))


def test_analysis_validation_and_edge_cases() -> None:
    stream = SymbolStream.from_text("ababa")
    boundaries = BoundaryConfiguration((2,), 5)
    assert NGramAnalysis(10).compute(stream, boundaries).counts == {}
    assert BlockComplexityAnalysis(10).compute(stream, boundaries).value == 0.0
    assert ForbiddenNGramAnalysis(2).compute(stream, boundaries).possible_count == 4
    assert 0 <= ForbiddenNGramFractionMetric(2).compute(stream, boundaries).value <= 1
    transition = TransitionAnalysis(2).compute(stream, boundaries)
    assert transition.sample_count == len(stream) - 2
    with pytest.raises(AnalysisInputError):
        NGramAnalysis(0)
    with pytest.raises(AnalysisInputError):
        NGramAnalysis(2, "bad").compute(stream, boundaries)  # type: ignore[arg-type]
    with pytest.raises(AnalysisInputError):
        TransitionAnalysis(3)
    with pytest.raises(AnalysisInputError):
        ForbiddenNGramAnalysis(5, max_possible_ngrams=2).compute(stream, boundaries)


def test_spectral_autocorrelation_and_metric_edges() -> None:
    stream = SymbolStream.from_text("abcdef")
    boundaries = BoundaryConfiguration((2, 4), 6)
    assert 0 <= BoundarySpectralEntropyMetric().compute(stream, boundaries).value <= 1
    assert (
        BoundarySpectrumAnalysis(detrend="none").compute(stream, boundaries).frequencies
    )
    assert (
        SegmentLengthSpectrumAnalysis().compute(stream, boundaries).units
        == "cycles per segment"
    )
    correlation = autocorrelation((1.0, 2.0, 3.0), max_lag=2)
    assert correlation.lags == (0, 1, 2)
    assert correlation.values[0] == pytest.approx(2 / 3)
    with pytest.raises(AnalysisInputError):
        autocorrelation(())
    with pytest.raises(AnalysisInputError):
        autocorrelation((1.0,), max_lag=1)
    with pytest.raises(AnalysisInputError):
        BoundarySpectrumAnalysis().compute(
            SymbolStream.from_text("x"), BoundaryConfiguration((), 1)
        )


def test_serialization_and_scalar_result_contracts() -> None:
    with pytest.raises(SerializationError):
        encode_uleb128(-1)
    with pytest.raises(SerializationError):
        canonical_json_bytes({"bad": math.inf})
    with pytest.raises(SerializationError):
        structural_stream_bytes(
            SymbolStream.from_text("ab"), BoundaryConfiguration((), 3)
        )
    with pytest.raises(MetricInputError):
        ScalarMetricResult("x", "1", math.nan, "x")
    assert empirical_p_value(2, [1, 2, 3], "less") == 3 / 4
    with pytest.raises(MetricInputError):
        empirical_p_value(1, [], "greater")
    with pytest.raises(MetricInputError):
        empirical_p_value(1, [1], "bad")  # type: ignore[arg-type]


def test_multiple_testing_references_and_validation() -> None:
    assert holm_adjust([0.01, 0.04, 0.03]) == pytest.approx((0.03, 0.06, 0.06))
    assert benjamini_hochberg_adjust([0.01, 0.04, 0.03]) == pytest.approx(
        (0.03, 0.04, 0.04)
    )
    assert holm_adjust([]) == ()
    assert benjamini_hochberg_adjust([]) == ()
    with pytest.raises(MetricInputError):
        holm_adjust([1.1])


def test_region_and_jitter_validation() -> None:
    region = Region("r", 0, 2)
    assert region.contains_internal(1)
    assert not region.contains_internal(2)
    region.validate_for_stream(2)
    with pytest.raises(InvalidRegionError):
        region.validate_for_stream(1)
    with pytest.raises(NullModelError):
        LocalJitterNullModel(-1)
    with pytest.raises(NullModelError):
        LocalJitterNullModel(1, 0)
    stream = SymbolStream.from_text("abcde")
    observed = BoundaryConfiguration((2,), 5)
    sample = LocalJitterNullModel(1).sample(stream, observed, np.random.default_rng(3))
    assert sample.count == observed.count
