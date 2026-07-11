"""Deterministic logical-slot null sample generation."""

import logging
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import numpy as np

from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import BoundaryAuditError, NullModelSamplingError
from boundary_audit.core.stream import SymbolStream
from boundary_audit.metrics.base import ScalarMetric
from boundary_audit.null_models.base import BoundaryNullModel

LOGGER = logging.getLogger("boundary_audit")


@dataclass(frozen=True, slots=True)
class SlotResult:
    """One accepted logical-slot value and its attempt count."""

    slot: int
    value: float
    attempts: int


@dataclass(frozen=True, slots=True)
class NullDistribution:
    """Ordered accepted values and aggregate retry accounting."""

    values: tuple[float, ...]
    total_attempts: int
    rejected_attempts: int


def evaluate_slot(
    *,
    slot: int,
    master_seed: int,
    max_attempts: int,
    stream: SymbolStream,
    observed: BoundaryConfiguration,
    metric: ScalarMetric,
    null_model: BoundaryNullModel,
) -> SlotResult:
    """Evaluate attempts for one slot with independent spawn keys."""
    for attempt in range(max_attempts):
        rng = np.random.default_rng(
            np.random.SeedSequence(entropy=master_seed, spawn_key=(slot, attempt))
        )
        try:
            candidate = null_model.sample(stream, observed, rng)
            if candidate.stream_length != len(stream):
                raise NullModelSamplingError(
                    "null model returned a mismatched stream length"
                )
            metric.validate_input(stream, candidate)
            value = metric.compute(stream, candidate).value
            if not math.isfinite(value):
                raise NullModelSamplingError("metric returned a non-finite value")
            return SlotResult(slot, value, attempt + 1)
        except BoundaryAuditError as error:
            LOGGER.debug("slot %d attempt %d rejected: %s", slot, attempt, error)
    LOGGER.error("slot %d exhausted %d attempts", slot, max_attempts)
    raise NullModelSamplingError(
        f"logical sample slot {slot} exhausted {max_attempts} attempts"
    )


def generate_null_distribution(
    *,
    stream: SymbolStream,
    observed: BoundaryConfiguration,
    metric: ScalarMetric,
    null_model: BoundaryNullModel,
    master_seed: int,
    n_samples: int,
    max_attempts: int,
    workers: int = 1,
) -> NullDistribution:
    """Generate values in logical-slot order regardless of completion order."""

    def run(slot: int) -> SlotResult:
        return evaluate_slot(
            slot=slot,
            master_seed=master_seed,
            max_attempts=max_attempts,
            stream=stream,
            observed=observed,
            metric=metric,
            null_model=null_model,
        )

    if workers < 1:
        raise NullModelSamplingError("workers must be at least 1")
    if workers == 1:
        results = tuple(run(slot) for slot in range(n_samples))
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = tuple(executor.map(run, range(n_samples)))
    values = tuple(result.value for result in results)
    total = sum(result.attempts for result in results)
    return NullDistribution(values, total, total - n_samples)
