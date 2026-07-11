"""Null-model comparison orchestration."""

import logging
import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

from boundary_audit import __version__
from boundary_audit.core.boundaries import BoundaryConfiguration
from boundary_audit.core.errors import MetricInputError, NullModelError
from boundary_audit.core.provenance import ExperimentSpec, create_experiment_spec
from boundary_audit.core.stream import SymbolStream
from boundary_audit.metrics.base import ScalarMetric
from boundary_audit.null_models.base import BoundaryNullModel
from boundary_audit.statistics.null_distribution import generate_null_distribution
from boundary_audit.statistics.pvalue import Alternative, empirical_p_value, z_score

LOGGER = logging.getLogger("boundary_audit")
Decision = Literal["reject_null", "fail_to_reject"]
EffectDirection = Literal["higher", "lower", "equal"]


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """Complete effect, decision, sampling, and provenance result."""

    experiment_id: str
    observed_value: float
    null_mean: float
    null_std: float
    raw_effect: float
    z_score: float
    empirical_p_value: float
    p_value_resolution: float
    effect_direction: EffectDirection
    decision: Decision
    significant: bool
    n_samples: int
    total_attempts: int
    rejected_attempts: int
    max_attempts_per_sample: int
    alternative: Alternative
    alpha: float
    spec: ExperimentSpec


class NullModelComparison:
    """Runner that owns all logical-slot and attempt randomness."""

    @staticmethod
    def run(
        *,
        stream: SymbolStream,
        observed: BoundaryConfiguration,
        metric: ScalarMetric,
        null_model: BoundaryNullModel,
        symbolization_id: str,
        n_samples: int,
        seed: int,
        alternative: Alternative = "two-sided",
        alpha: float = 0.05,
        max_attempts_per_sample: int = 100,
        workers: int = 1,
    ) -> ComparisonResult:
        """Compare one observed scalar with exactly n accepted null values."""
        if n_samples < 2:
            raise MetricInputError("n_samples must be at least 2")
        if max_attempts_per_sample < 1:
            raise MetricInputError("max_attempts_per_sample must be at least 1")
        if not 0.0 < alpha < 1.0 or not math.isfinite(alpha):
            raise MetricInputError("alpha must be finite and strictly between 0 and 1")
        if not symbolization_id.strip():
            raise MetricInputError(
                "symbolization_id must be non-empty and not whitespace"
            )
        metric.validate_input(stream, observed)
        missing = (
            metric.requirements.required_null_invariants
            - null_model.capabilities.guaranteed_invariants
        )
        if missing:
            names = ", ".join(sorted(invariant.value for invariant in missing))
            raise NullModelError(
                f"null model does not guarantee required invariants: {names}"
            )
        observed_value = metric.compute(stream, observed).value
        spec = create_experiment_spec(
            stream=stream,
            observed=observed,
            symbolization_id=symbolization_id,
            metric_id=metric.id,
            metric_version=metric.version,
            metric_parameters=metric.parameters(),
            null_model_id=null_model.id,
            null_model_version=null_model.version,
            null_model_parameters=null_model.parameters(),
            package_version=__version__,
            master_seed=seed,
            n_samples=n_samples,
            max_attempts_per_sample=max_attempts_per_sample,
            alternative=alternative,
            alpha=alpha,
        )
        LOGGER.info("comparison %s started", spec.experiment_id)
        distribution = generate_null_distribution(
            stream=stream,
            observed=observed,
            metric=metric,
            null_model=null_model,
            master_seed=seed,
            n_samples=n_samples,
            max_attempts=max_attempts_per_sample,
            workers=workers,
        )
        null_mean = float(np.mean(distribution.values))
        null_std = float(np.std(distribution.values, ddof=1))
        raw_effect = observed_value - null_mean
        direction: EffectDirection = (
            "higher" if raw_effect > 0.0 else "lower" if raw_effect < 0.0 else "equal"
        )
        p_value = empirical_p_value(observed_value, distribution.values, alternative)
        significant = p_value <= alpha
        decision: Decision = "reject_null" if significant else "fail_to_reject"
        result = ComparisonResult(
            spec.experiment_id,
            observed_value,
            null_mean,
            null_std,
            raw_effect,
            z_score(observed_value, null_mean, null_std),
            p_value,
            1.0 / (n_samples + 1),
            direction,
            decision,
            significant,
            n_samples,
            distribution.total_attempts,
            distribution.rejected_attempts,
            max_attempts_per_sample,
            alternative,
            alpha,
            spec,
        )
        LOGGER.info("comparison %s completed", spec.experiment_id)
        return result
