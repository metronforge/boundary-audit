"""Experimental public API for boundary-audit."""

import logging
from importlib.metadata import version

__version__ = version("boundary-audit")

logging.getLogger(__name__).addHandler(logging.NullHandler())

from boundary_audit.analyses.autocorrelation import (  # noqa: E402
    AutocorrelationResult,
    autocorrelation,
)
from boundary_audit.analyses.block_complexity import (  # noqa: E402
    BlockComplexityAnalysis,
    FiniteSampleBlockComplexity,
)
from boundary_audit.analyses.entropy_rate import (  # noqa: E402
    ConditionalEntropyAnalysis,
    ConditionalEntropyResult,
)
from boundary_audit.analyses.forbidden import (  # noqa: E402
    ForbiddenNGramAnalysis,
    ForbiddenNGramResult,
)
from boundary_audit.analyses.ngrams import NGramAnalysis, NGramResult  # noqa: E402
from boundary_audit.analyses.segment_lengths import (  # noqa: E402
    SegmentLengthAnalysis,
    SegmentLengthSummary,
)
from boundary_audit.analyses.spectra import (  # noqa: E402
    BoundarySpectrumAnalysis,
    SegmentLengthSpectrumAnalysis,
    SpectrumResult,
)
from boundary_audit.analyses.transitions import (  # noqa: E402
    TransitionAnalysis,
    TransitionResult,
)
from boundary_audit.core.alphabet import Alphabet  # noqa: E402
from boundary_audit.core.boundaries import BoundaryConfiguration  # noqa: E402
from boundary_audit.core.errors import (  # noqa: E402
    AnalysisInputError,
    BoundaryAuditError,
    BoundaryOutOfRangeError,
    EmptyStreamError,
    InvalidBoundaryConfigurationError,
    InvalidRegionError,
    InvalidSymbolError,
    MetricInputError,
    NonFiniteMetricError,
    NullModelError,
    NullModelSamplingError,
    SerializationError,
)
from boundary_audit.core.provenance import ExperimentSpec  # noqa: E402
from boundary_audit.core.regions import Region  # noqa: E402
from boundary_audit.core.stream import SymbolStream  # noqa: E402
from boundary_audit.metrics.base import ScalarMetricResult  # noqa: E402
from boundary_audit.metrics.boundary_pair_mi import (  # noqa: E402
    BoundaryPairMutualInformationMetric,
)
from boundary_audit.metrics.boundary_spectral_entropy import (  # noqa: E402
    BoundarySpectralEntropyMetric,
)
from boundary_audit.metrics.compression_ratio import (  # noqa: E402
    CompressionRatioMetric,
    CompressionResult,
    compression_result,
)
from boundary_audit.metrics.forbidden_fraction import (  # noqa: E402
    ForbiddenNGramFractionMetric,
)
from boundary_audit.metrics.positional_entropy_difference import (  # noqa: E402
    PositionalEntropyDifferenceMetric,
    PositionalEntropyResult,
    positional_entropies,
)
from boundary_audit.metrics.segment_length_entropy import (  # noqa: E402
    SegmentLengthEntropyMetric,
)
from boundary_audit.metrics.segment_length_variance import (  # noqa: E402
    SegmentLengthVarianceMetric,
)
from boundary_audit.null_models.base import (  # noqa: E402
    BoundaryInvariant,
    NullModelCapabilities,
)
from boundary_audit.null_models.blockwise_fixed_count import (  # noqa: E402
    BlockwiseFixedCountNullModel,
)
from boundary_audit.null_models.empirical_renewal import (  # noqa: E402
    EmpiricalRenewalNullModel,
)
from boundary_audit.null_models.fixed_count_uniform import (  # noqa: E402
    FixedCountUniformNullModel,
)
from boundary_audit.null_models.length_permutation import (  # noqa: E402
    LengthPermutationNullModel,
)
from boundary_audit.null_models.local_jitter import LocalJitterNullModel  # noqa: E402
from boundary_audit.statistics.comparison import (  # noqa: E402
    ComparisonResult,
    NullModelComparison,
)
from boundary_audit.statistics.multiple_testing import (  # noqa: E402
    benjamini_hochberg_adjust,
    holm_adjust,
)
from boundary_audit.transforms.remove_all import RemoveAllBoundaries  # noqa: E402

__all__ = [
    "__version__",
    "Alphabet",
    "AnalysisInputError",
    "AutocorrelationResult",
    "BlockComplexityAnalysis",
    "BlockwiseFixedCountNullModel",
    "BoundaryAuditError",
    "BoundaryConfiguration",
    "BoundaryInvariant",
    "BoundaryOutOfRangeError",
    "BoundaryPairMutualInformationMetric",
    "BoundarySpectralEntropyMetric",
    "BoundarySpectrumAnalysis",
    "ComparisonResult",
    "CompressionRatioMetric",
    "CompressionResult",
    "ConditionalEntropyAnalysis",
    "ConditionalEntropyResult",
    "EmptyStreamError",
    "EmpiricalRenewalNullModel",
    "ExperimentSpec",
    "FiniteSampleBlockComplexity",
    "FixedCountUniformNullModel",
    "ForbiddenNGramAnalysis",
    "ForbiddenNGramFractionMetric",
    "ForbiddenNGramResult",
    "InvalidBoundaryConfigurationError",
    "InvalidRegionError",
    "InvalidSymbolError",
    "LengthPermutationNullModel",
    "LocalJitterNullModel",
    "MetricInputError",
    "NGramAnalysis",
    "NGramResult",
    "NonFiniteMetricError",
    "NullModelCapabilities",
    "NullModelComparison",
    "NullModelError",
    "NullModelSamplingError",
    "PositionalEntropyDifferenceMetric",
    "PositionalEntropyResult",
    "Region",
    "RemoveAllBoundaries",
    "ScalarMetricResult",
    "SegmentLengthAnalysis",
    "SegmentLengthEntropyMetric",
    "SegmentLengthSpectrumAnalysis",
    "SegmentLengthSummary",
    "SegmentLengthVarianceMetric",
    "SerializationError",
    "SpectrumResult",
    "SymbolStream",
    "TransitionAnalysis",
    "TransitionResult",
    "autocorrelation",
    "benjamini_hochberg_adjust",
    "compression_result",
    "holm_adjust",
    "positional_entropies",
]
