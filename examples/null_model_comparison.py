"""Reproducible fixed-count Monte Carlo comparison."""

from boundary_audit import (
    BoundaryConfiguration,
    BoundaryPairMutualInformationMetric,
    FixedCountUniformNullModel,
    NullModelComparison,
    SymbolStream,
)

stream = SymbolStream.from_text("abacabadabacaba")
observed = BoundaryConfiguration((3, 7, 11), len(stream))
result = NullModelComparison.run(
    stream=stream,
    observed=observed,
    metric=BoundaryPairMutualInformationMetric(),
    null_model=FixedCountUniformNullModel(),
    symbolization_id="python-codepoint-v1",
    n_samples=100,
    seed=42,
    alternative="greater",
)
assert result.total_attempts == result.n_samples + result.rejected_attempts
