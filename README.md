# timeseries-gap

**Efficient missing timestamp detection for regularly sampled time series.**

`timeseries-gap` is a lightweight Python library for detecting missing timestamps in regularly sampled time series.

It is designed to work with ordered or unordered data, identify missing intervals, detect duplicate timestamps, and provide detailed information about data completeness.

The library has no runtime dependencies and supports Python 3.10 and later.

## Features

- Detect missing timestamps in regularly sampled time series.
- Identify internal, leading, and trailing gaps.
- Support unordered input with automatic sorting.
- Support pre-sorted input for efficient processing.
- Detect and count duplicate timestamps.
- Validate timestamp types, intervals, and alignment.
- Configure explicit analysis boundaries.
- Set limits on input size and the number of missing ranges.
- Represent missing timestamps as compact ranges.
- Iterate over missing timestamps lazily.
- Materialize missing timestamps with an explicit size limit.
- Return immutable analysis results.

## Installation

```bash
pip install timeseries-gap
```

## Quick start

```python
from timeseries_gap import analyze

timestamps = [0, 60, 180, 240]

result = analyze(
    timestamps,
    interval=60,
)

print(result.missing_ranges)
# ((120, 120),)

print(result.missing_count)
# 1

print(result.completeness)
# 80.0

print(result.missing_percentage)
# 20.0
```

The library detects that timestamp `120` is missing from the expected sequence.

## Usage examples

### 1. Unordered input

Input timestamps do not need to be sorted.

```python
from timeseries_gap import analyze

timestamps = [240, 0, 180, 60]

result = analyze(timestamps, interval=60)

print(result.missing_ranges)
# ((120, 120),)
```

By default, the library sorts the input before analysis.

### 2. Explicit analysis boundaries

Without explicit boundaries, only internal gaps can be detected.

To include missing timestamps at the beginning or end of a series, provide both `start` and `end`.

```python
from timeseries_gap import analyze

timestamps = [120, 180, 240]

result = analyze(
    timestamps,
    interval=60,
    start=0,
    end=300,
)

print(result.missing_ranges)
# ((0, 60), (300, 300))
```

Both boundaries are inclusive.

### 3. Pre-sorted input

When timestamps are already sorted, use `assume_sorted=True`.

```python
from timeseries_gap import analyze

timestamps = [0, 60, 180, 240]

result = analyze(
    timestamps,
    interval=60,
    assume_sorted=True,
)
```

This avoids creating and sorting an additional list of input timestamps. The input must be nondecreasing.

### 4. Duplicate timestamps

Duplicate timestamps are ignored when calculating the number of present timestamps, but they are counted separately.

```python
from timeseries_gap import analyze

timestamps = [0, 60, 60, 120, 240]

result = analyze(timestamps, interval=60)

print(result.present_count)
# 4

print(result.duplicate_count)
# 1

print(result.missing_ranges)
# ((180, 180),)
```

### 5. Resource limits

Optional limits help control resource consumption.

```python
from timeseries_gap import analyze

result = analyze(
    [0, 60, 180, 240],
    interval=60,
    max_input_items=100_000,
    max_gap_ranges=1_000,
)
```

- `max_input_items`: maximum number of input items accepted.
- `max_gap_ranges`: maximum number of separate missing ranges allowed.

Both parameters default to `None`, meaning no explicit limit.

## API reference

### `analyze()`

```python
analyze(
    timestamps,
    *,
    interval,
    start=None,
    end=None,
    assume_sorted=False,
    max_input_items=None,
    max_gap_ranges=None,
)
```

| Parameter | Description |
|---|---|
| `timestamps` | Iterable of integer timestamps |
| `interval` | Positive sampling interval |
| `start` | Optional inclusive start boundary |
| `end` | Optional inclusive end boundary |
| `assume_sorted` | Whether input is already sorted |
| `max_input_items` | Optional maximum input size |
| `max_gap_ranges` | Optional maximum number of missing ranges |

Both `start` and `end` must be provided together.

Timestamps, boundaries, and intervals must be integers. Boolean values are not accepted as integers.

### `GapResult`

`analyze()` returns an immutable `GapResult` object.

| Attribute or method | Description |
|---|---|
| `missing_ranges` | Tuple of missing timestamp ranges |
| `expected_count` | Total expected timestamps |
| `present_count` | Number of unique present timestamps |
| `duplicate_count` | Number of duplicate input timestamps |
| `interval` | Sampling interval |
| `missing_count` | Total number of missing timestamps |
| `gap_count` | Number of separate missing ranges |
| `completeness` | Percentage of expected timestamps present |
| `missing_percentage` | Percentage of expected timestamps missing |
| `iter_missing_timestamps()` | Lazy iterator over missing timestamps |
| `to_timestamps(max_items=...)` | Materializes missing timestamps with a required size limit |

When no timestamps are expected, percentage properties return `None`.

### Compact missing ranges

Missing timestamps are stored as ranges rather than individual values.

For example:

```python
missing_ranges = (
    (120, 300),
    (600, 720),
)
```

With an interval of 60, these ranges represent:

```text
120, 180, 240, 300
600, 660, 720
```

This representation avoids storing every missing timestamp individually.

### Lazy iteration

Use `iter_missing_timestamps()` when processing missing timestamps without creating a complete list in memory.

```python
for timestamp in result.iter_missing_timestamps():
    print(timestamp)
```

### Controlled materialization

Use `to_timestamps()` when a list is required.

```python
missing = result.to_timestamps(max_items=10_000)
```

The operation raises `MaterializationLimitExceededError` if the number of missing timestamps exceeds the specified limit.

## Exceptions

All library exceptions inherit from `TimeseriesGapError`.

| Exception | Description |
|---|---|
| `TimeseriesGapError` | Base exception |
| `InvalidTimestampError` | Invalid timestamp type or value |
| `InvalidIntervalError` | Invalid sampling interval |
| `InvalidRangeError` | Invalid analysis boundaries |
| `MisalignedTimestampError` | Timestamp does not belong to the expected grid |
| `TimestampOutOfRangeError` | Timestamp falls outside explicit boundaries |
| `UnsortedInputError` | Input is not sorted when sorted input is required |
| `InputLimitExceededError` | Maximum input size exceeded |
| `GapRangeLimitExceededError` | Maximum number of missing ranges exceeded |
| `MaterializationLimitExceededError` | Materialization limit exceeded |

Example:

```python
from timeseries_gap import (
    InvalidIntervalError,
    analyze,
)

try:
    result = analyze([0, 60, 120], interval=0)
except InvalidIntervalError as error:
    print(error)
```

## Potential use cases

`timeseries-gap` can be used in different domains where data is expected at regular time intervals.

Examples include:

- Financial market data validation.
- Cryptocurrency OHLCV candle verification.
- Sensor data quality monitoring.
- IoT time series.
- Industrial monitoring.
- Data ingestion and ETL pipelines.
- Historical time series integrity checks.

For example, a cryptocurrency data pipeline can use the library to identify missing one-minute candles before performing historical analysis or backtesting.

## Development

Clone the repository:

```bash
git clone https://github.com/lucanegrianalyst/timeseries-gap.git
cd timeseries-gap
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
python -m pytest
```

Run code quality checks:

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
```

## Project status

`timeseries-gap` is an early-stage project.

The public API and implementation are under active development.

Contributions, bug reports, and suggestions are welcome.

## License

This project is licensed under the Apache License 2.0.

See the `LICENSE` file for details.
