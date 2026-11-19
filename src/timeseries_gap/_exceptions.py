"""Custom exceptions exposed by timeseries-gap."""


class TimeseriesGapError(Exception):
    """Base exception for all timeseries-gap errors."""


class InvalidTimestampError(TimeseriesGapError):
    """Raised when a timestamp has an invalid type or value."""


class InvalidIntervalError(TimeseriesGapError):
    """Raised when the sampling interval is invalid."""


class InvalidRangeError(TimeseriesGapError):
    """Raised when the requested analysis range is invalid."""


class MisalignedTimestampError(TimeseriesGapError):
    """Raised when a timestamp does not belong to the expected grid."""


class TimestampOutOfRangeError(TimeseriesGapError):
    """Raised when a timestamp falls outside the requested range."""


class UnsortedInputError(TimeseriesGapError):
    """Raised when sorted input was requested but timestamps decrease."""


class InputLimitExceededError(TimeseriesGapError):
    """Raised when the maximum number of input items is exceeded."""


class GapRangeLimitExceededError(TimeseriesGapError):
    """Raised when the maximum number of missing ranges is exceeded."""


class MaterializationLimitExceededError(TimeseriesGapError):
    """Raised when expanding missing timestamps would exceed the limit."""
