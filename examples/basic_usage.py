"""Basic immutable domain-model usage."""

from boundary_audit import BoundaryConfiguration, SegmentLengthAnalysis, SymbolStream

stream = SymbolStream.from_text("qokedy")
boundaries = BoundaryConfiguration((2, 4), len(stream))
summary = SegmentLengthAnalysis().compute(stream, boundaries)
assert summary.lengths == (2, 2, 2)
