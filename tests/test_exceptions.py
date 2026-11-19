import pytest

from timeseries_gap._exceptions import (
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


@pytest.mark.parametrize(
    "exception",
    [
        InvalidTimestampError,
        InvalidIntervalError,
        InvalidRangeError,
        MisalignedTimestampError,
        TimestampOutOfRangeError,
        UnsortedInputError,
        InputLimitExceededError,
        GapRangeLimitExceededError,
        MaterializationLimitExceededError,
    ],
)
def test_all_exceptions_inherit_from_base(exception):
    assert issubclass(exception, TimeseriesGapError)


def test_base_exception_inherits_from_exception():
    assert issubclass(TimeseriesGapError, Exception)


def test_specific_exception_can_be_caught_by_base():
    with pytest.raises(TimeseriesGapError):
        raise MisalignedTimestampError("Invalid timestamp alignment")


def test_exception_preserves_error_message():
    message = "Invalid interval"

    with pytest.raises(InvalidIntervalError, match=message):
        raise InvalidIntervalError(message)
