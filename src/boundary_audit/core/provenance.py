"""Deterministic experiment provenance."""

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import MetricInputError
from boundary_audit.core.serialization import (
    boundary_bytes,
    canonical_json_bytes,
    exact_stream_bytes,
    structural_stream_bytes,
)
from boundary_audit.core.stream import SymbolStream
from boundary_audit.core.types import JSONValue
from boundary_audit.utils.hashing import sha256_hex

P_VALUE_CONVENTION = "add_one_empirical_central_distance_v1"
RNG_ALGORITHM = "numpy.default_rng(SeedSequence(entropy=seed,spawn_key=(slot,attempt)))"
NUMERICAL_CONVENTION_VERSION = "1"


@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    """Complete deterministic snapshot governing one comparison."""

    exact_stream_hash: str
    structural_pattern_hash: str
    observed_boundary_hash: str
    symbolization_id: str
    metric_id: str
    metric_version: str
    metric_parameters: dict[str, JSONValue]
    null_model_id: str
    null_model_version: str
    null_model_parameters: dict[str, JSONValue]
    package_version: str
    master_seed: int
    n_samples: int
    max_attempts_per_sample: int
    alternative: str
    alpha: float
    p_value_convention: str = P_VALUE_CONVENTION
    rng_algorithm: str = RNG_ALGORITHM
    numerical_convention_version: str = NUMERICAL_CONVENTION_VERSION

    def __post_init__(self) -> None:
        if not self.symbolization_id.strip():
            raise MetricInputError(
                "symbolization_id must be non-empty and not whitespace"
            )

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical JSON for experiment hashing."""
        raw = asdict(self)
        value: dict[str, JSONValue] = json.loads(json.dumps(raw, allow_nan=False))
        return canonical_json_bytes(value)

    @property
    def experiment_id(self) -> str:
        """Return deterministic SHA-256 over the complete canonical snapshot."""
        return sha256_hex(self.canonical_bytes())


def create_experiment_spec(
    *,
    stream: SymbolStream,
    observed: BoundaryConfiguration,
    symbolization_id: str,
    metric_id: str,
    metric_version: str,
    metric_parameters: Mapping[str, JSONValue],
    null_model_id: str,
    null_model_version: str,
    null_model_parameters: Mapping[str, JSONValue],
    package_version: str,
    master_seed: int,
    n_samples: int,
    max_attempts_per_sample: int,
    alternative: str,
    alpha: float,
) -> ExperimentSpec:
    """Construct hashes and copied parameter mappings for one comparison."""
    return ExperimentSpec(
        exact_stream_hash=sha256_hex(exact_stream_bytes(stream)),
        structural_pattern_hash=sha256_hex(
            structural_stream_bytes(stream, BoundaryConfiguration((), len(stream)))
        ),
        observed_boundary_hash=sha256_hex(boundary_bytes(observed)),
        symbolization_id=symbolization_id,
        metric_id=metric_id,
        metric_version=metric_version,
        metric_parameters=dict(metric_parameters),
        null_model_id=null_model_id,
        null_model_version=null_model_version,
        null_model_parameters=dict(null_model_parameters),
        package_version=package_version,
        master_seed=master_seed,
        n_samples=n_samples,
        max_attempts_per_sample=max_attempts_per_sample,
        alternative=alternative,
        alpha=alpha,
    )
