from hypothesis import given
from hypothesis import strategies as st

from timeseries_gap import analyze


@st.composite
def regular_series(draw):
    """Generate a non-empty subset of a regular timestamp grid."""
    interval = draw(st.integers(min_value=1, max_value=1000))
    origin = draw(st.integers(min_value=-100_000, max_value=100_000))
    count = draw(st.integers(min_value=1, max_value=100))

    present_indices = draw(
        st.sets(
            st.integers(min_value=0, max_value=count - 1),
            min_size=1,
        )
    )

    timestamps = [origin + index * interval for index in sorted(present_indices)]

    return interval, timestamps


@given(regular_series())
def test_generated_series_preserves_count_invariants(case):
    interval, timestamps = case

    result = analyze(timestamps, interval=interval)

    expected = set(range(min(timestamps), max(timestamps) + interval, interval))
    present = set(timestamps)
    missing = set(result.iter_missing_timestamps())

    assert result.expected_count == len(expected)
    assert result.present_count == len(present)
    assert result.missing_count == len(expected - present)
    assert result.expected_count == result.present_count + result.missing_count
    assert missing == expected - present


@given(regular_series(), st.data())
def test_generated_duplicates_do_not_change_missing_ranges(case, data):
    interval, timestamps = case

    duplicates = data.draw(
        st.lists(
            st.sampled_from(timestamps),
            max_size=50,
        )
    )

    original = analyze(timestamps, interval=interval)
    with_duplicates = analyze(
        [*timestamps, *duplicates],
        interval=interval,
    )

    assert with_duplicates.missing_ranges == original.missing_ranges
    assert with_duplicates.expected_count == original.expected_count
    assert with_duplicates.present_count == original.present_count
    assert with_duplicates.duplicate_count == len(duplicates)


@given(regular_series(), st.data())
def test_generated_input_order_does_not_change_result(case, data):
    interval, timestamps = case

    shuffled = data.draw(st.permutations(timestamps))

    normal = analyze(timestamps, interval=interval)
    unordered = analyze(shuffled, interval=interval)

    assert unordered.missing_ranges == normal.missing_ranges
    assert unordered.expected_count == normal.expected_count
    assert unordered.present_count == normal.present_count
    assert unordered.duplicate_count == normal.duplicate_count


@given(regular_series())
def test_generated_sorted_mode_matches_normal_mode(case):
    interval, timestamps = case

    normal = analyze(timestamps, interval=interval)
    sorted_mode = analyze(
        timestamps,
        interval=interval,
        assume_sorted=True,
    )

    assert sorted_mode.missing_ranges == normal.missing_ranges
    assert sorted_mode.expected_count == normal.expected_count
    assert sorted_mode.present_count == normal.present_count
    assert sorted_mode.duplicate_count == normal.duplicate_count


@given(
    interval=st.integers(min_value=1, max_value=1000),
    origin=st.integers(min_value=-100_000, max_value=100_000),
    count=st.integers(min_value=1, max_value=100),
    data=st.data(),
)
def test_generated_explicit_range_preserves_invariants(
    interval,
    origin,
    count,
    data,
):
    present_indices = data.draw(
        st.sets(
            st.integers(min_value=0, max_value=count - 1),
            min_size=0,
        )
    )

    start = origin
    end = origin + (count - 1) * interval

    timestamps = [origin + index * interval for index in sorted(present_indices)]

    result = analyze(
        timestamps,
        interval=interval,
        start=start,
        end=end,
    )

    expected = set(range(start, end + interval, interval))
    present = set(timestamps)
    missing = set(result.iter_missing_timestamps())

    assert result.expected_count == count
    assert result.present_count == len(present)
    assert result.missing_count == len(expected - present)
    assert result.expected_count == result.present_count + result.missing_count
    assert missing == expected - present
