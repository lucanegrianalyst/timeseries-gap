
"""Memory usage benchmark for timeseries-gap."""

import gc
import tracemalloc

from timeseries_gap import analyze


def measure_memory(size: int, shuffled: bool = False) -> None:
    timestamps = list(range(0, size * 60, 60))

    if shuffled:
        import random

        random.Random(42).shuffle(timestamps)

    gc.collect()
    tracemalloc.start()

    before, _ = tracemalloc.get_traced_memory()

    result = analyze(
        timestamps,
        interval=60,
        assume_sorted=not shuffled,
    )

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(
        f"{size:>9,} timestamp | "
        f"{'casuali' if shuffled else 'ordinati':>8} | "
        f"picco aggiuntivo: {(peak - before) / (1024 * 1024):.2f} MB | "
        f"memoria finale aggiuntiva: {(current - before) / (1024 * 1024):.2f} MB | "
        f"timestamp mancanti: {result.missing_count}"
    )


def main() -> None:
    print("Benchmark memoria - timeseries-gap")
    print("-" * 85)

    for size in (100_000, 500_000):
        measure_memory(size, shuffled=False)
        measure_memory(size, shuffled=True)


if __name__ == "__main__":
    main()
