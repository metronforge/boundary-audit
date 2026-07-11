# Implementation Plan

The phases below follow specification section 35. Each phase is complete only
after formatting, linting, strict type checking, and its relevant tests pass.

| Phase | Specification | Production modules | Metamorphic relations | Reference / contract tests | Acceptance criteria |
|---|---|---|---|---|---|
| 1. Tooling and skeleton | §§7, 29–32 | `pyproject.toml`, package exports, logging, pre-commit, CI | N/A | wheel install and version smoke test | AC 1, 19 |
| 2. Immutable core and serialization | §§4–10, 19 | `core/{stream,boundaries,segments,alphabet,regions,errors,types,serialization}.py`, `utils/hashing.py` | MR-CORE-001..006, MR-MET-006..007 | Boundary round trips, ULEB128 and exact framing; invalid symbols, positions, regions | AC 2, 11, 12, 18 |
| 3. Transforms and null models | §§11–13 | `transforms/*`, `null_models/*` | MR-NULL-001..009 | Invalid/impossible model contracts | AC 3–6 |
| 4. Provenance and deterministic slots | §§13, 22–24 | `core/provenance.py`, `statistics/{null_distribution,comparison,pvalue}.py` | MR-STAT-001..008 | Empirical p-values, insufficient samples, non-finite retry | AC 4, 5, 13, 14, 21, 22 |
| 5. Analysis and metric protocols | §§14–15 | `analyses/base.py`, `metrics/{base,requirements}.py` | MR-STAT-008 | Protocol and capability contracts | AC 6–8 |
| 6. Scalar metrics | §18 | `metrics/{segment_length_variance,segment_length_entropy,positional_entropy_difference,boundary_pair_mi,forbidden_fraction,boundary_spectral_entropy,compression_ratio}.py` | MR-MET-001..007 | Manual entropy and MI | AC 7, 8, 11 |
| 7. Symbolic dynamics | §§16–17 | `analyses/{segment_lengths,ngrams,forbidden,transitions,entropy_rate,block_complexity}.py` | MR-DYN-001..005 | Enumeration limits and minimum observations | AC 9 |
| 8. Spectral analyses | §§20–21 | `analyses/{spectra,autocorrelation}.py`, `utils/numeric.py` | MR-SPEC-001..006 | Independent FFT/Parseval case | AC 10 |
| 9. Multiple testing | §22.5 | `statistics/multiple_testing.py` | Order/permutation and monotonicity follow-ups | Hand-calculated Holm and BH examples | AC 15 |
| 10. Full verification and documentation | §§25–36 | examples, README, CHANGELOG, CI | Full MR suite review | Contract and integration suites; clean wheel install | AC 16–20 |

General float comparisons use `rtol=1e-12`, `atol=1e-12`; spectral tests use
`rtol=1e-10`, `atol=1e-12`. Hypothesis generates source and follow-up cases.
Reference tests do not call the production helper they independently anchor.
