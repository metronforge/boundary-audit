"""Explicit multi-character symbols and exact reconstruction."""

from boundary_audit import BoundaryConfiguration, SymbolStream

stream = SymbolStream.from_symbols(["qo", "k", "e", "d", "y"])
boundaries = BoundaryConfiguration((2,), len(stream))
assert boundaries.segments(stream) == (("qo", "k"), ("e", "d", "y"))
assert stream.to_symbols() == ("qo", "k", "e", "d", "y")
