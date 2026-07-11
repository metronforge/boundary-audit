from boundary_audit import (
    BoundaryConfiguration,
    ComparisonResult,
    FixedCountUniformNullModel,
    NullModelComparison,
    SegmentLengthVarianceMetric,
    SymbolStream,
)


def test_comparison_is_reproducible_and_attempt_accounting_is_exact() -> None:
    stream = SymbolStream.from_text("abcdefghijkl")
    observed = BoundaryConfiguration((3, 7, 9), len(stream))

    def run() -> ComparisonResult:
        return NullModelComparison.run(
            stream=stream,
            observed=observed,
            metric=SegmentLengthVarianceMetric(),
            null_model=FixedCountUniformNullModel(),
            symbolization_id="unicode-codepoint-v1",
            n_samples=20,
            seed=123,
        )

    result = run()
    assert result == run()
    assert result.total_attempts == result.n_samples + result.rejected_attempts
    assert result.p_value_resolution == 1 / 21
