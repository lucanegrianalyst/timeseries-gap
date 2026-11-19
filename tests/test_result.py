import pytest

from timeseries_gap._exceptions import MaterializationLimitExceededError
from timeseries_gap._models import GapResult


@pytest.fixture
def result():
    return GapResult(
        missing_ranges=((20, 40), (80, 80)),
        expected_count=6,
        present_count=3,
        duplicate_count=1,
        interval=20,
    )


def test_missing_count(result):
    assert result.missing_count == 3


def test_gap_count(result):
    assert result.gap_count == 2


def test_completeness(result):
    assert result.completeness == 50.0


def test_missing_percentage(result):
    assert result.missing_percentage == 50.0


def test_iter_missing_timestamps(result):
    assert list(result.iter_missing_timestamps()) == [20, 40, 80]


def test_to_timestamps(result):
    assert result.to_timestamps(max_items=3) == [20, 40, 80]


def test_materialization_limit(result):
    with pytest.raises(MaterializationLimitExceededError):
        result.to_timestamps(max_items=2)


def test_zero_materialization_limit_with_no_gaps():
    empty = GapResult(
        missing_ranges=(),
        expected_count=3,
        present_count=3,
        duplicate_count=0,
        interval=10,
    )

    assert empty.to_timestamps(max_items=0) == []


def test_result_is_immutable(result):
    with pytest.raises((AttributeError, TypeError)):
        result.interval = 10


def test_missing_ranges_are_immutable(result):
    assert isinstance(result.missing_ranges, tuple)
    assert all(isinstance(item, tuple) for item in result.missing_ranges)


def test_duplicate_count(result):
    assert result.duplicate_count == 1


@pytest.mark.parametrize("max_items", [True, 1.5, "10", None])
def test_to_timestamps_rejects_invalid_max_items(max_items):
    result = GapResult(
        missing_ranges=((10, 10),),
        expected_count=2,
        present_count=1,
        duplicate_count=0,
        interval=10,
    )

    with pytest.raises(TypeError):
        result.to_timestamps(max_items=max_items)


def test_to_timestamps_rejects_negative_max_items():
    result = GapResult(
        missing_ranges=((10, 10),),
        expected_count=2,
        present_count=1,
        duplicate_count=0,
        interval=10,
    )

    with pytest.raises(ValueError):
        result.to_timestamps(max_items=-1)


def make_result(**overrides):
    values = {
        "missing_ranges": ((10, 10),),
        "expected_count": 2,
        "present_count": 1,
        "duplicate_count": 0,
        "interval": 10,
    }
    values.update(overrides)
    return GapResult(**values)


@pytest.mark.parametrize("interval", [0, -1, True, 1.5])
def test_rejects_invalid_interval(interval):
    with pytest.raises(ValueError):
        make_result(interval=interval)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("expected_count", -1),
        ("expected_count", True),
        ("present_count", -1),
        ("present_count", 1.5),
        ("duplicate_count", -1),
        ("duplicate_count", False),
    ],
)
def test_rejects_invalid_counts(field, value):
    with pytest.raises(ValueError):
        make_result(**{field: value})


def test_rejects_non_tuple_missing_ranges():
    with pytest.raises(ValueError):
        make_result(missing_ranges=[[10, 10]])


def test_rejects_invalid_range_structure():
    with pytest.raises(ValueError):
        make_result(missing_ranges=((10, 10, 20),))


@pytest.mark.parametrize(
    "missing_ranges",
    [
        ((True, 10),),
        ((10, 10.5),),
        ((20, 10),),
        ((10, 15),),
    ],
)
def test_rejects_invalid_range_endpoints(missing_ranges):
    with pytest.raises(ValueError):
        make_result(missing_ranges=missing_ranges)


@pytest.mark.parametrize(
    "missing_ranges",
    [
        ((10, 20), (20, 30)),
        ((10, 20), (30, 30)),
        ((30, 30), (10, 10)),
    ],
)
def test_rejects_overlapping_adjacent_or_unordered_ranges(missing_ranges):
    with pytest.raises(ValueError):
        make_result(
            missing_ranges=missing_ranges,
            expected_count=4,
            present_count=1,
        )


def test_rejects_ranges_on_different_grids():
    with pytest.raises(ValueError):
        make_result(
            missing_ranges=((10, 10), (21, 21)),
            expected_count=3,
            present_count=1,
        )


def test_rejects_inconsistent_counts():
    with pytest.raises(ValueError):
        make_result(expected_count=3)


def test_rejects_duplicates_without_present_timestamps():
    with pytest.raises(ValueError):
        make_result(
            missing_ranges=((10, 20),),
            expected_count=2,
            present_count=0,
            duplicate_count=1,
        )
