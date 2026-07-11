"""Structured boundary-indicator spectrum."""

from boundary_audit import BoundaryConfiguration, BoundarySpectrumAnalysis, SymbolStream

stream = SymbolStream.from_text("abcdefghijklmnop")
boundaries = BoundaryConfiguration((2, 4, 6, 8, 10, 12, 14), len(stream))
spectrum = BoundarySpectrumAnalysis(top_k=3).compute(stream, boundaries)
assert 0.0 <= spectrum.spectral_entropy <= 1.0
