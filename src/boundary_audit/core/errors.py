"""Typed exceptions raised by boundary-audit."""


class BoundaryAuditError(Exception):
    """Base class for package domain errors."""


class EmptyStreamError(BoundaryAuditError):
    """Raised when a symbol stream is empty."""


class InvalidSymbolError(BoundaryAuditError):
    """Raised when a symbol is not a non-empty string."""


class InvalidBoundaryConfigurationError(BoundaryAuditError):
    """Raised when boundary positions are not strictly increasing."""


class BoundaryOutOfRangeError(InvalidBoundaryConfigurationError):
    """Raised when a boundary is outside the stream's internal gaps."""


class InvalidRegionError(BoundaryAuditError):
    """Raised for an invalid half-open region."""


class MetricInputError(BoundaryAuditError):
    """Raised when a scalar metric's preconditions are not met."""


class AnalysisInputError(BoundaryAuditError):
    """Raised when a structured analysis's preconditions are not met."""


class NullModelError(BoundaryAuditError):
    """Raised for an invalid null-model definition or use."""


class NullModelSamplingError(NullModelError):
    """Raised when a null model cannot produce a valid sample."""


class NonFiniteMetricError(MetricInputError):
    """Raised when a scalar metric returns NaN or infinity."""


class SerializationError(BoundaryAuditError):
    """Raised when canonical serialization cannot be performed."""
