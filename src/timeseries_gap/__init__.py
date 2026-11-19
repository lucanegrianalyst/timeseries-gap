"""Public API for timeseries-gap."""

from ._core import analyze
from ._exceptions import (
    GapRangeLimitExceededError,
    InputLimitExceededError,
    InvalidIntervalError,
    InvalidRangeError,
    InvalidTimestampError,
    MaterializationLimitExceededError,
    MisalignedTimestampError,
    TimeseriesGapError,
    TimestampOutOfRangeError,
    UnsortedInputError,
)
from ._models import GapResult

__all__ = [
    "GapRangeLimitExceededError",
    "GapResult",
    "InputLimitExceededError",
    "InvalidIntervalError",
    "InvalidRangeError",
    "InvalidTimestampError",
    "MaterializationLimitExceededError",
    "MisalignedTimestampError",
    "TimeseriesGapError",
    "TimestampOutOfRangeError",
    "UnsortedInputError",
    "analyze",
]
