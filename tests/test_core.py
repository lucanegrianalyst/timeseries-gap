import pytest

from timeseries_gap import analyze
from timeseries_gap._exceptions import (
    GapRangeLimitExceededError,
    InputLimitExceededError,
    InvalidIntervalError,
    InvalidRangeError,
    InvalidTimestampError,
    MisalignedTimestampError,
    TimestampOutOfRangeError,
    UnsortedInputError,
)


def test_detect_internal_gaps():
    result = analyze([0, 60, 240], interval=60)

    assert result.missing_ranges == ((120, 180),)
    assert result.missing_count == 2
    assert result.expected_count == 5
    assert result.present_count == 3


def test_complete_series_has_no_gaps():
    result = analyze([0, 60, 120], interval=60)

    assert result.missing_ranges == ()
    assert result.missing_count == 0
    assert result.completeness == 100.0


def test_unsorted_input_is_sorted_automatically():
    result = analyze([120, 0, 60], interval=60)

    assert result.missing_ranges == ()
    assert result.present_count == 3


def test_duplicates_are_removed_and_counted():
    result = analyze([0, 60, 60, 120, 120], interval=60)

    assert result.present_count == 3
    assert result.duplicate_count == 2
    assert result.missing_count == 0


def test_sorted_mode_accepts_duplicates():
    result = analyze([0, 60, 60, 120], interval=60, assume_sorted=True)

    assert result.present_count == 3
    assert result.duplicate_count == 1


def test_sorted_mode_rejects_decreasing_timestamp():
    with pytest.raises(UnsortedInputError):
        analyze([0, 120, 60], interval=60, assume_sorted=True)


def test_generator_input():
    timestamps = (value for value in [0, 120, 240])

    result = analyze(timestamps, interval=60)

    assert result.missing_ranges == ((60, 60), (180, 180))


def test_empty_input_without_range():
    result = analyze([], interval=60)

    assert result.expected_count == 0
    assert result.present_count == 0
    assert result.missing_count == 0
    assert result.completeness is None
    assert result.missing_percentage is None


def test_single_timestamp():
    result = analyze([120], interval=60)

    assert result.expected_count == 1
    assert result.present_count == 1
    assert result.completeness == 100.0


def test_explicit_range_includes_leading_and_trailing_gaps():
    result = analyze([60, 120], interval=60, start=0, end=180)

    assert result.missing_ranges == ((0, 0), (180, 180))
    assert result.expected_count == 4
    assert result.present_count == 2


def test_empty_input_with_explicit_range():
    result = analyze([], interval=60, start=0, end=120)

    assert result.missing_ranges == ((0, 120),)
    assert result.missing_count == 3
    assert result.expected_count == 3
    assert result.present_count == 0
    assert result.completeness == 0.0


def test_negative_timestamps():
    result = analyze([-120, 0], interval=60)

    assert result.missing_ranges == ((-60, -60),)


def test_start_without_end_is_invalid():
    with pytest.raises(InvalidRangeError):
        analyze([0, 60], interval=60, start=0)


def test_end_without_start_is_invalid():
    with pytest.raises(InvalidRangeError):
        analyze([0, 60], interval=60, end=60)


def test_end_before_start_is_invalid():
    with pytest.raises(InvalidRangeError):
        analyze([], interval=60, start=120, end=60)


@pytest.mark.parametrize("interval", [0, -1, True, False, 1.5, "60", None])
def test_invalid_interval(interval):
    with pytest.raises(InvalidIntervalError):
        analyze([0, 60], interval=interval)


@pytest.mark.parametrize("timestamp", [True, False, 1.5, "60", None])
def test_invalid_timestamp(timestamp):
    with pytest.raises(InvalidTimestampError):
        analyze([timestamp], interval=60)


def test_misaligned_timestamp():
    with pytest.raises(MisalignedTimestampError):
        analyze([0, 61, 120], interval=60)


def test_misaligned_explicit_end():
    with pytest.raises(MisalignedTimestampError):
        analyze([0], interval=60, start=0, end=90)


def test_timestamp_before_explicit_range():
    with pytest.raises(TimestampOutOfRangeError):
        analyze([0, 60], interval=60, start=60, end=120)


def test_timestamp_after_explicit_range():
    with pytest.raises(TimestampOutOfRangeError):
        analyze([60, 180], interval=60, start=0, end=120)


def test_input_limit_counts_duplicates():
    with pytest.raises(InputLimitExceededError):
        analyze([0, 0, 60], interval=60, max_input_items=2)


def test_input_limit_allows_exact_limit():
    result = analyze([0, 60], interval=60, max_input_items=2)

    assert result.present_count == 2


def test_zero_input_limit_accepts_empty_input():
    result = analyze([], interval=60, max_input_items=0)

    assert result.expected_count == 0


def test_zero_input_limit_rejects_nonempty_input():
    with pytest.raises(InputLimitExceededError):
        analyze([0], interval=60, max_input_items=0)


def test_gap_range_limit():
    with pytest.raises(GapRangeLimitExceededError):
        analyze([0, 120, 240], interval=60, max_gap_ranges=1)


def test_zero_gap_range_limit_with_no_gaps():
    result = analyze([0, 60, 120], interval=60, max_gap_ranges=0)

    assert result.gap_count == 0


def test_zero_gap_range_limit_with_a_gap():
    with pytest.raises(GapRangeLimitExceededError):
        analyze([0, 120], interval=60, max_gap_ranges=0)


@pytest.mark.parametrize("value", [1, "yes", None])
def test_assume_sorted_must_be_boolean(value):
    with pytest.raises(TypeError):
        analyze([0, 60], interval=60, assume_sorted=value)


@pytest.mark.parametrize("value", [True, -1, 1.5, "10"])
def test_invalid_max_input_items(value):
    with pytest.raises(ValueError):
        analyze([0], interval=60, max_input_items=value)


@pytest.mark.parametrize("value", [True, -1, 1.5, "10"])
def test_invalid_max_gap_ranges(value):
    with pytest.raises(ValueError):
        analyze([0], interval=60, max_gap_ranges=value)


def test_timestamp_grid_is_relative_to_explicit_start():
    result = analyze(
        [-120, -60, 60, 120],
        interval=60,
        start=-120,
        end=120,
    )

    assert result.missing_ranges == ((0, 0),)


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (True, 60),
        (0, 60.5),
        (0, "60"),
    ],
)
def test_invalid_explicit_range_types(start, end):
    with pytest.raises(InvalidRangeError):
        analyze([], interval=60, start=start, end=end)
