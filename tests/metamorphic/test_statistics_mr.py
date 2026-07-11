import pytest
from hypothesis import given
from hypothesis import strategies as st

from boundary_audit import (
    BoundaryConfiguration,
    ComparisonResult,
    FixedCountUniformNullModel,
    NullModelComparison,
    SegmentLengthVarianceMetric,
    SymbolStream,
)
from boundary_audit.statistics.pvalue import empirical_p_value, z_score

finite_lists = st.lists(st.integers(-100, 100).map(float), min_size=2, max_size=20)


@given(finite_lists, st.floats(-100, 100, allow_nan=False, allow_infinity=False))
def test_mr_stat_001_permutation_changes_nothing(
    values: list[float], observed: float
) -> None:
    assert empirical_p_value(observed, values, "two-sided") == empirical_p_value(
        observed, list(reversed(values)), "two-sided"
    )


@given(
    finite_lists,
    st.floats(-100, 100, allow_nan=False, allow_infinity=False),
    st.floats(-10, 10, allow_nan=False, allow_infinity=False),
)
def test_mr_stat_002_additive_shift_preserves_p_and_z(
    values: list[float], observed: float, shift: float
) -> None:
    mean = sum(values) / len(values)
    std = float(__import__("numpy").std(values, ddof=1))
    assert empirical_p_value(observed, values, "greater") == empirical_p_value(
        observed + shift, [x + shift for x in values], "greater"
    )
    assert z_score(observed, mean, std) == pytest.approx(
        z_score(observed + shift, mean + shift, std)
    )


@given(
    finite_lists,
    st.floats(-100, 100, allow_nan=False, allow_infinity=False),
    st.floats(0.1, 10, allow_nan=False, allow_infinity=False),
)
def test_mr_stat_003_positive_scale_preserves_p(
    values: list[float], observed: float, scale: float
) -> None:
    assert empirical_p_value(observed, values, "greater") == empirical_p_value(
        observed * scale, [x * scale for x in values], "greater"
    )


@given(
    finite_lists,
    st.floats(-100, 100, allow_nan=False, allow_infinity=False),
    st.floats(0, 20, allow_nan=False, allow_infinity=False),
)
def test_mr_stat_004_greater_tail_monotone(
    values: list[float], observed: float, delta: float
) -> None:
    assert empirical_p_value(observed + delta, values, "greater") <= empirical_p_value(
        observed, values, "greater"
    )


@given(st.floats(-100, 100, allow_nan=False, allow_infinity=False), st.integers(2, 20))
def test_mr_stat_005_equality_gives_p_one(value: float, n: int) -> None:
    assert empirical_p_value(value, [value] * n, "two-sided") == 1.0


def test_mr_stat_006_007_same_spec_and_parallel_result() -> None:
    stream = SymbolStream.from_text("abcabcabc")
    observed = BoundaryConfiguration((3, 6), len(stream))

    def run(workers: int) -> ComparisonResult:
        return NullModelComparison.run(
            stream=stream,
            observed=observed,
            metric=SegmentLengthVarianceMetric(),
            null_model=FixedCountUniformNullModel(),
            symbolization_id="char-v1",
            n_samples=12,
            seed=42,
            workers=workers,
        )

    sequential = run(1)
    parallel = run(3)
    assert sequential == parallel
    assert sequential.experiment_id == parallel.experiment_id
