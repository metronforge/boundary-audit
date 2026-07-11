import math

import numpy as np
import pytest

from boundary_audit import (
    BoundaryConfiguration,
    BoundaryPairMutualInformationMetric,
    SymbolStream,
)
from boundary_audit.core.serialization import (
    encode_uleb128,
    exact_stream_bytes,
    structural_stream_bytes,
)
from boundary_audit.statistics.pvalue import empirical_p_value
from boundary_audit.utils.numeric import entropy_bits


def test_manual_entropy_reference() -> None:
    assert entropy_bits(("a", "a", "b", "b")) == 1.0
    assert entropy_bits(("a", "a", "a", "b")) == pytest.approx(
        -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
    )


def test_manual_mutual_information_reference() -> None:
    stream = SymbolStream.from_text("abab")
    boundaries = BoundaryConfiguration((1, 3), 4)
    assert BoundaryPairMutualInformationMetric().compute(
        stream, boundaries
    ).value == pytest.approx(0.9182958340544896)


def test_empirical_p_value_reference() -> None:
    values = [1.0, 2.0, 3.0, 4.0]
    assert empirical_p_value(3.0, values, "greater") == 3 / 5
    assert empirical_p_value(3.0, values, "less") == 4 / 5


def test_fft_parseval_reference() -> None:
    x = np.array([1.0, -1.0, 1.0, -1.0])
    transformed = np.fft.rfft(x)
    one_sided = np.abs(transformed) ** 2 / 16
    one_sided[1:-1] *= 2
    assert sum(one_sided) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("value", "encoded"),
    [
        (0, b"\x00"),
        (1, b"\x01"),
        (127, b"\x7f"),
        (128, b"\x80\x01"),
        (255, b"\xff\x01"),
        (256, b"\x80\x02"),
        (16383, b"\xff\x7f"),
        (16384, b"\x80\x80\x01"),
    ],
)
def test_uleb128_reference(value: int, encoded: bytes) -> None:
    assert encode_uleb128(value) == encoded


def test_exact_and_structural_framing_reference() -> None:
    left = SymbolStream.from_symbols(["qo", "k"])
    right = SymbolStream.from_symbols(["q", "ok"])
    boundaries = BoundaryConfiguration((1,), 2)
    assert exact_stream_bytes(left) != exact_stream_bytes(right)
    assert structural_stream_bytes(left, boundaries) == structural_stream_bytes(
        right, boundaries
    )
