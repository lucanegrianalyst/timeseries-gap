
"""Performance benchmarks for timeseries-gap."""

import random

import pyperf

from timeseries_gap import analyze


def analyze_sorted(timestamps):
    """Benchmark analysis of sorted timestamps."""
    return analyze(timestamps, interval=60, assume_sorted=True)


def analyze_unsorted(timestamps):
    """Benchmark analysis of shuffled timestamps."""
    return analyze(timestamps, interval=60, assume_sorted=False)


def main() -> None:
    runner = pyperf.Runner()

    sizes = (100_000, 500_000)

    for size in sizes:
        timestamps = list(range(0, size * 60, 60))

        timestamps_unsorted = timestamps.copy()
        random.Random(42).shuffle(timestamps_unsorted)

        runner.bench_func(
            f"analyze_sorted_{size}",
            analyze_sorted,
            timestamps,
        )

        runner.bench_func(
            f"analyze_unsorted_{size}",
            analyze_unsorted,
            timestamps_unsorted,
        )


if __name__ == "__main__":
    main()
