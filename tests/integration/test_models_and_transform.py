import numpy as np

from boundary_audit import (
    BlockwiseFixedCountNullModel,
    BoundaryConfiguration,
    Region,
    RemoveAllBoundaries,
    SegmentLengthAnalysis,
    SymbolStream,
)
from boundary_audit.core.segments import boundaries_from_segment_lengths


def test_blockwise_model_transform_and_helpers() -> None:
    stream = SymbolStream.from_text("abcdefghij")
    observed = BoundaryConfiguration((1, 3, 5, 8, 9), 10)
    model = BlockwiseFixedCountNullModel((Region("left", 1, 5), Region("right", 5, 9)))
    sampled = model.sample(stream, observed, np.random.default_rng(42))
    assert sampled.count == observed.count
    assert {1, 5, 9}.issubset(sampled.positions)
    assert model.parameters()["regions"]
    assert RemoveAllBoundaries().apply(stream, observed).positions == ()
    assert boundaries_from_segment_lengths((2, 3, 5)).positions == (2, 5)
    assert (
        SegmentLengthAnalysis().compute(stream, observed).count
        == observed.segment_count
    )
