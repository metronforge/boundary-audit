# boundary-audit

`boundary-audit` is an experimental, domain-neutral Python library for
mathematical and statistical analysis of supplied boundary configurations in
finite symbolic streams. It evaluates whether an observed configuration is
extreme only relative to an explicit symbolization, scalar metric, null model,
and statistical procedure. It does not infer semantic meaning.

Requires Python 3.11 or newer.

## Core model

A `SymbolStream` contains caller-supplied, non-empty string symbols. Boundary
positions index those symbols, including when symbols contain multiple
characters. `to_symbols()` is exact; `to_text()` is only a display helper.

```python
from boundary_audit import BoundaryConfiguration, SymbolStream

stream = SymbolStream.from_symbols(["qo", "k", "e", "d", "y"])
boundaries = BoundaryConfiguration((2,), stream_length=len(stream))
assert boundaries.segments(stream) == (("qo", "k"), ("e", "d", "y"))
```

## Reproducible comparisons

`NullModelComparison` owns randomness. Logical slot `i` and candidate attempt
`j` receive an independent NumPy generator from
`SeedSequence(entropy=master_seed, spawn_key=(i, j))`. Results are stored in
logical slot order, so sequential and parallel evaluation are identical;
retries in one slot cannot perturb any other slot.

Metrics declare required null invariants, and null models declare capabilities
they guarantee for every successful sample. Compatibility is checked before
the first random sample, then each candidate is dynamically validated.

```python
from boundary_audit import (
    BoundaryPairMutualInformationMetric,
    FixedCountUniformNullModel,
    NullModelComparison,
)

result = NullModelComparison.run(
    stream=stream,
    observed=boundaries,
    metric=BoundaryPairMutualInformationMetric(),
    null_model=FixedCountUniformNullModel(),
    symbolization_id="explicit-symbols-v1",
    n_samples=1000,
    seed=42,
    alternative="greater",
)
```

`symbolization_id` is a required, non-empty, caller-controlled opaque identifier
for the external convention used to construct the stream. The library does not
interpret it or guarantee uniqueness. It is part of deterministic provenance
and therefore changes the experiment ID.

The add-one estimator has
`p_value_resolution = 1 / (n_samples + 1)`. `fail_to_reject` means only that the
configured test did not reject its null; it is not acceptance of the null
hypothesis. In a successful result, `total_attempts` counts all accepted and
rejected generation/evaluation attempts across slots, while
`rejected_attempts` counts only unsuccessful attempts. Consequently,
`total_attempts = n_samples + rejected_attempts`.

## Canonical serialization

Structural serialization encodes first-observed symbol IDs plus boundary
records, making compression invariant under bijective symbol renaming. Exact
serialization frames each UTF-8 symbol spelling and length, so `['qo', 'k']`
and `['q', 'ok']` have different provenance hashes despite identical joined
text. Both use the shared `BAUD` header, version byte, tagged records, and
arbitrary-precision unsigned LEB128 integers.

## Scientific and numerical conventions

Structured analyses are separate from scalar metrics. Spectra use float64,
rectangular windows, `rfft`, one-sided Parseval-consistent power, and mean
detrending by default. Rectangular windows can exhibit spectral leakage.
Empirical p-values use add-one greater, less, or central-distance two-sided
formulas. Null standard deviation uses `ddof=1`.

## Development and releases

```bash
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
mypy --strict src tests
pytest --cov=boundary_audit --cov-branch
```

The project follows Semantic Versioning derived from Conventional Commits.
Python Semantic Release updates the single version in `pyproject.toml`, updates
`CHANGELOG.md`, creates the Git tag and GitHub Release, and attaches built
distributions. Keep history linear and rebase branches before integration. See
`CONTRIBUTING.md` for commit-message rules.

Status: experimental API, version 0.1.0.
