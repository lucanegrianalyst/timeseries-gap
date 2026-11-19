"""Core timestamp gap analysis implementation."""

from collections.abc import Iterable, Iterator

from ._exceptions import (
    GapRangeLimitExceededError,
    InputLimitExceededError,
    InvalidIntervalError,
    InvalidRangeError,
    InvalidTimestampError,
    MisalignedTimestampError,
    TimestampOutOfRangeError,
    UnsortedInputError,
)
from ._models import GapResult


def _validate_integer(value: object, name: str) -> bool:
    """Return whether a value is an integer but not a boolean."""
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_limit(value: int | None, name: str) -> None:
    """Validate an optional non-negative integer resource limit."""
    if value is None:
        return

    if not _validate_integer(value, name) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer or None")


def _validated_input(
    timestamps: Iterable[int],
    max_input_items: int | None,
    assume_sorted: bool,
) -> Iterator[int]:
    """Validate timestamps and optionally verify nondecreasing order."""
    previous: int | None = None
    for count, timestamp in enumerate(timestamps, start=1):
        if max_input_items is not None and count > max_input_items:
            raise InputLimitExceededError(f"Input contains more than {max_input_items} items")

        if not _validate_integer(timestamp, "timestamp"):
            raise InvalidTimestampError(
                f"Timestamp must be an integer, not {type(timestamp).__name__}"
            )

        if assume_sorted and previous is not None and timestamp < previous:
            raise UnsortedInputError(f"Input is not sorted: {timestamp} follows {previous}")

        previous = timestamp
        yield timestamp


def _append_gap(
    ranges: list[tuple[int, int]],
    gap_start: int,
    gap_end: int,
    max_gap_ranges: int | None,
) -> None:
    """Append a missing range while enforcing the configured limit."""
    if gap_start > gap_end:
        return

    if max_gap_ranges is not None and len(ranges) >= max_gap_ranges:
        raise GapRangeLimitExceededError(f"More than {max_gap_ranges} missing ranges were found")

    ranges.append((gap_start, gap_end))


def _build_result(
    timestamps: Iterable[int],
    interval: int,
    start: int | None,
    end: int | None,
    max_gap_ranges: int | None,
) -> GapResult:
    """Build a result from nondecreasing, validated timestamps."""
    ranges: list[tuple[int, int]] = []
    origin = start
    previous: int | None = None
    present_count = 0
    duplicate_count = 0

    for timestamp in timestamps:
        if start is not None and end is not None and (timestamp < start or timestamp > end):
            raise TimestampOutOfRangeError(f"Timestamp {timestamp} is outside [{start}, {end}]")

        if origin is None:
            origin = timestamp

        if (timestamp - origin) % interval != 0:
            raise MisalignedTimestampError(
                f"Timestamp {timestamp} is not aligned to interval {interval}"
            )

        if previous is not None and timestamp == previous:
            duplicate_count += 1
            continue

        if previous is None:
            if start is not None and timestamp > start:
                _append_gap(
                    ranges,
                    start,
                    timestamp - interval,
                    max_gap_ranges,
                )
        elif timestamp > previous + interval:
            _append_gap(
                ranges,
                previous + interval,
                timestamp - interval,
                max_gap_ranges,
            )

        previous = timestamp
        present_count += 1

    if start is None and previous is None:
        return GapResult(
            missing_ranges=(),
            expected_count=0,
            present_count=0,
            duplicate_count=duplicate_count,
            interval=interval,
        )

    if start is not None and end is not None:
        if previous is None:
            _append_gap(ranges, start, end, max_gap_ranges)
        elif previous < end:
            _append_gap(
                ranges,
                previous + interval,
                end,
                max_gap_ranges,
            )
        effective_start = start
        effective_end = end
    else:
        assert origin is not None
        assert previous is not None
        effective_start = origin
        effective_end = previous

    expected_count = ((effective_end - effective_start) // interval) + 1

    return GapResult(
        missing_ranges=tuple(ranges),
        expected_count=expected_count,
        present_count=present_count,
        duplicate_count=duplicate_count,
        interval=interval,
    )


def analyze(
    timestamps: Iterable[int],
    *,
    interval: int,
    start: int | None = None,
    end: int | None = None,
    assume_sorted: bool = False,
    max_input_items: int | None = None,
    max_gap_ranges: int | None = None,
) -> GapResult:
    """Analyze a regularly sampled time series for missing timestamps."""
    if not _validate_integer(interval, "interval") or interval <= 0:
        raise InvalidIntervalError("interval must be a positive integer")

    if not isinstance(assume_sorted, bool):
        raise TypeError("assume_sorted must be a boolean")

    _validate_limit(max_input_items, "max_input_items")
    _validate_limit(max_gap_ranges, "max_gap_ranges")

    if (start is None) != (end is None):
        raise InvalidRangeError("start and end must either both be supplied or both omitted")

    if start is not None and (
        not _validate_integer(start, "start") or not _validate_integer(end, "end")
    ):
        raise InvalidRangeError("start and end must be integers")

    if start is not None and end is not None:
        if end < start:
            raise InvalidRangeError("end must be greater than or equal to start")

        if (end - start) % interval != 0:
            raise MisalignedTimestampError(
                "The explicit end is not aligned with start and interval"
            )

    validated = _validated_input(
        timestamps,
        max_input_items,
        assume_sorted,
    )

    if assume_sorted:
        ordered = validated
    else:
        ordered_values = list(validated)
        ordered_values.sort()
        ordered = iter(ordered_values)

    return _build_result(
        ordered,
        interval,
        start,
        end,
        max_gap_ranges,
    )
