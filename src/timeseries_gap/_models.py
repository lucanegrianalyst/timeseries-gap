"""Immutable result models for timeseries-gap."""

from collections.abc import Iterator
from dataclasses import dataclass

from ._exceptions import MaterializationLimitExceededError


@dataclass(frozen=True, slots=True)
class GapResult:
    """Immutable summary of missing timestamps in a time series."""

    missing_ranges: tuple[tuple[int, int], ...]
    expected_count: int
    present_count: int
    duplicate_count: int
    interval: int

    def __post_init__(self) -> None:
        """Validate the consistency of the result."""
        integer_fields = {
            "expected_count": self.expected_count,
            "present_count": self.present_count,
            "duplicate_count": self.duplicate_count,
            "interval": self.interval,
        }

        for name, value in integer_fields.items():
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")

        if self.interval <= 0:
            raise ValueError("interval must be positive")

        for name in ("expected_count", "present_count", "duplicate_count"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")

        if not isinstance(self.missing_ranges, tuple):
            raise ValueError("missing_ranges must be a tuple")

        previous_end: int | None = None
        missing_count = 0
        grid_origin: int | None = None

        for item in self.missing_ranges:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ValueError("Each missing range must be a tuple of two integers")

            start, end = item

            if any(isinstance(value, bool) or not isinstance(value, int) for value in item):
                raise ValueError("Missing range endpoints must be integers")

            if start > end:
                raise ValueError("Missing range start must not exceed its end")

            if (end - start) % self.interval != 0:
                raise ValueError("Missing range length must align with interval")

            if grid_origin is None:
                grid_origin = start
            elif (start - grid_origin) % self.interval != 0:
                raise ValueError("Missing ranges must belong to the same timestamp grid")

            if previous_end is not None and start <= previous_end + self.interval:
                raise ValueError("Missing ranges must be ordered, separate, and non-adjacent")

            missing_count += ((end - start) // self.interval) + 1
            previous_end = end

        if self.expected_count != self.present_count + missing_count:
            raise ValueError("expected_count must equal present_count plus missing timestamps")

        if self.duplicate_count > 0 and self.present_count == 0:
            raise ValueError("Duplicates cannot exist without present timestamps")

    @property
    def missing_count(self) -> int:
        """Return the total number of missing timestamps."""
        return sum(((end - start) // self.interval) + 1 for start, end in self.missing_ranges)

    @property
    def gap_count(self) -> int:
        """Return the number of separate missing ranges."""
        return len(self.missing_ranges)

    @property
    def completeness(self) -> float | None:
        """Return the percentage of expected timestamps that are present."""
        if self.expected_count == 0:
            return None
        return self.present_count / self.expected_count * 100

    @property
    def missing_percentage(self) -> float | None:
        """Return the percentage of expected timestamps that are missing."""
        if self.expected_count == 0:
            return None
        return self.missing_count / self.expected_count * 100

    def iter_missing_timestamps(self) -> Iterator[int]:
        """Yield missing timestamps lazily, in ascending order."""
        for start, end in self.missing_ranges:
            current = start
            while current <= end:
                yield current
                current += self.interval

    def to_timestamps(self, *, max_items: int) -> list[int]:
        """Materialize missing timestamps, enforcing an explicit size limit."""
        if isinstance(max_items, bool) or not isinstance(max_items, int):
            raise TypeError("max_items must be a non-negative integer")

        if max_items < 0:
            raise ValueError("max_items must be a non-negative integer")

        missing_count = self.missing_count
        if missing_count > max_items:
            raise MaterializationLimitExceededError(
                f"Materializing {missing_count} timestamps exceeds the limit of {max_items}"
            )

        return list(self.iter_missing_timestamps())
