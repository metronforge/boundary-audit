import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from boundary_audit.analyses.spectra import power_spectrum

arrays = st.lists(
    st.floats(-100, 100, allow_nan=False, allow_infinity=False), min_size=2, max_size=30
).map(tuple)


@given(arrays)
def test_mr_spec_001_reversal_preserves_power(values: tuple[float, ...]) -> None:
    assert power_spectrum(values, units="x").power == pytest.approx(
        power_spectrum(tuple(reversed(values)), units="x").power, rel=1e-10, abs=1e-12
    )


@given(arrays, st.integers(-100, 100))
def test_mr_spec_002_circular_shift_preserves_power(
    values: tuple[float, ...], shift: int
) -> None:
    shifted = tuple(np.roll(values, shift))
    assert power_spectrum(values, units="x").power == pytest.approx(
        power_spectrum(shifted, units="x").power, rel=1e-10, abs=1e-12
    )


@given(arrays, st.floats(0.1, 10, allow_nan=False, allow_infinity=False))
def test_mr_spec_003_004_scaling_power_and_entropy(
    values: tuple[float, ...], scale: float
) -> None:
    source = power_spectrum(values, units="x")
    follow = power_spectrum(tuple(scale * x for x in values), units="x")
    assert follow.power == pytest.approx(
        tuple(scale * scale * p for p in source.power), rel=1e-10, abs=1e-12
    )
    assert follow.spectral_entropy == pytest.approx(
        source.spectral_entropy, rel=1e-10, abs=1e-12
    )


@given(arrays, st.floats(-100, 100, allow_nan=False, allow_infinity=False))
def test_mr_spec_005_mean_detrend_removes_constant(
    values: tuple[float, ...], constant: float
) -> None:
    source = power_spectrum(values, units="x")
    follow = power_spectrum(tuple(x + constant for x in values), units="x")
    assert source.power[1:] == pytest.approx(follow.power[1:], rel=1e-10, abs=1e-12)


@given(arrays)
def test_mr_spec_006_parseval(values: tuple[float, ...]) -> None:
    centered = np.asarray(values) - np.mean(values)
    assert sum(power_spectrum(values, units="x").power) == pytest.approx(
        float(np.mean(centered**2)), rel=1e-10, abs=1e-12
    )
