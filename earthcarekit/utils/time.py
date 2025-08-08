import datetime
from dataclasses import dataclass
from typing import Any, Iterable, Literal, Sequence, TypeAlias

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray

TimestampLike: TypeAlias = (
    str | np.str_ | pd.Timestamp | np.datetime64 | datetime.datetime
)

TimedeltaLike: TypeAlias = (
    str | np.str_ | pd.Timedelta | np.timedelta64 | datetime.timedelta
)

TimeRangeLike: TypeAlias = (
    tuple[TimestampLike, TimestampLike] | list[TimestampLike] | NDArray[np.datetime64]
)


def validate_time_range(
    time_range: TimeRangeLike | None,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Checks if given `time_range` is valid, if True returns is as a `tuple`
    of two `pandas.Timestamp`s, if False raises `ValueError`.
    """
    if isinstance(time_range, (Iterable, np.ndarray)):
        if len(time_range) == 2:
            if all([isinstance(t, TimestampLike) for t in time_range]):
                result_time_range: tuple[pd.Timestamp, pd.Timestamp] = (
                    to_timestamp(time_range[0]),
                    to_timestamp(time_range[1]),
                )
                if result_time_range[0] <= result_time_range[1]:
                    return result_time_range
                else:
                    raise ValueError(
                        f"time range needs to increase monotonically, got instead: {tuple([str(t) for t in time_range])}"
                    )
    raise ValueError(f"invalid time range: {time_range}")


def time_to_string(time: TimestampLike, format: str = "%Y-%m-%dT%H:%M:%S") -> str:
    """Converts timestamp into a formatted string (defaults to YYYY-MM-DDTHH:MM:SS)."""
    timestamp = to_timestamp(time)
    if isinstance(timestamp, pd.Timestamp):
        return timestamp.strftime(format)
    else:
        return ""


def time_to_iso(
    time: TimestampLike,
    format: Literal["datetime", "date", "time"] | str = "datetime",
) -> str:
    """Converts timestamp into an ISO-formatted string.

    Args:
        time (TimestampLike): The input timestamp.
        format (Literal["date", "time", "datetime"]): The type of ISO string to return:
            - "datetime" -> YYYY-MM-DDTHH:MM:SS (default)
            - "date" -> YYYY-MM-DD
            - "time" -> HH:MM:SS

    Returns:
        str: ISO-formatted string corresponding to the requested type.
    """
    if not isinstance(format, str):
        raise TypeError(
            f"""Invalid type for output_format '{type(format).__name__}', expected Literal["date", "time", "datetime"]"""
        )
    if format == "date":
        return time_to_string(time, "%Y-%m-%d")
    elif format == "time":
        return time_to_string(time, "%H:%M:%S")
    elif format == "datetime":
        return time_to_string(time, "%Y-%m-%dT%H:%M:%S")
    else:
        return time_to_string(time, format)


def to_timestamp(t: TimestampLike, keep_tzinfo: bool = False) -> pd.Timestamp:
    """Converts input to `pandas.Timestamp`."""
    if isinstance(t, np.str_):
        t = str(t)

    if isinstance(t, TimestampLike):
        new_t = pd.Timestamp(t)
        if not keep_tzinfo and new_t.tzinfo is not None:
            new_t = new_t.tz_convert(None)
        return new_t
    else:
        raise TypeError(f"Input timestamp has invalud type ({type(t)}: {t})")


def to_timestamps(
    times: pd.DatetimeIndex | Sequence[TimestampLike] | ArrayLike,
    keep_tzinfo: bool = False,
) -> pd.DatetimeIndex:
    """Converts inputs to `pandas.Timestamp`s and returns them as `pandas.DatetimeIndex`."""
    if isinstance(times, pd.DatetimeIndex):
        return times
    if isinstance(times, (Sequence, np.ndarray)):
        return pd.DatetimeIndex(
            [to_timestamp(t, keep_tzinfo=keep_tzinfo) for t in times]
        )
    else:
        raise TypeError(f"Input timestamps has invalid type ({type(times)}: {times})")


def to_timedelta(t: TimedeltaLike) -> pd.Timedelta:
    """Converts input to `pandas.Timedelta`."""
    if isinstance(t, np.str_):
        t = str(t)

    if isinstance(t, TimedeltaLike):
        return pd.Timedelta(t)
    else:
        raise TypeError(f"Input timedelta has invalud type ({type(t)}: {t})")


def to_timedeltas(times: Sequence[TimedeltaLike] | NDArray) -> pd.TimedeltaIndex:
    """Converts inputs to `pandas.Timedelta`s and returns them as `pandas.TimedeltaIndex`."""
    if isinstance(times, (Sequence | np.ndarray)):
        return pd.TimedeltaIndex([to_timedelta(t) for t in times])
    else:
        raise TypeError(f"Input timestamps has invalud type ({type(times)}: {times})")


def format_time_range_text(
    st: TimestampLike, et: TimestampLike, show_date: bool = True, show_time: bool = True
) -> str:
    """Returns a formatted text label (`str`) describing the time range given by the start time `st` and end time `et`."""
    st = to_timestamp(st)
    et = to_timestamp(et)

    if (
        st.year == et.year
        and st.month == et.month
        and st.day == et.day
        and st.hour == et.hour
        and st.minute == et.minute
    ):
        texts = []
        if show_date:
            texts.append(f"{st.day} {st.strftime('%b')} {st.year}")
        if show_time:
            texts.append(f"{str(st.hour).zfill(2)}:{str(st.minute).zfill(2)} UTC")
        return ", ".join(texts)

    if (
        st.year == et.year
        and st.month == et.month
        and st.day == et.day
        and st.hour == et.hour
    ):
        texts = []
        if show_date:
            texts.append(f"{st.day} {st.strftime('%b')} {st.year}")
        if show_time:
            texts.append(
                f"{str(st.hour).zfill(2)}:{str(st.minute).zfill(2)}-{str(et.minute).zfill(2)} UTC"
            )
        return ", ".join(texts)

    if st.year == et.year and st.month == et.month and st.day == et.day:
        texts = []
        if show_date:
            texts.append(f"{st.day} {st.strftime('%b')} {st.year}")
        if show_time:
            texts.append(
                f"{str(st.hour).zfill(2)}:{str(st.minute).zfill(2)}-{str(et.hour).zfill(2)}:{str(et.minute).zfill(2)} UTC"
            )
        return ", ".join(texts)

    if st.year == et.year and st.month == et.month:
        if show_time:
            return f"{st.strftime('%b')} {st.year}, {st.day} {str(st.hour).zfill(2)}:{str(st.minute).zfill(2)} - {et.day} {str(et.hour).zfill(2)}:{str(et.minute).zfill(2)} UTC"
        if show_date:
            return f"{st.day}-{et.day} {st.strftime('%b')} {st.year}"

    if st.year == et.year:
        if show_time:
            return f"{st.year}, {st.strftime('%b')} {st.day} {str(st.hour).zfill(2)}:{str(st.minute).zfill(2)} - {et.strftime('%b')} {et.day} {str(et.hour).zfill(2)}:{str(et.minute).zfill(2)} UTC"
        if show_date:
            return (
                f"{st.day} {st.strftime('%b')} - {et.day} {et.strftime('%b')} {st.year}"
            )
    else:
        if show_time:
            return f"{st.day} {st.strftime('%b')} {st.year} {str(st.hour).zfill(2)}:{str(st.minute).zfill(2)} - {et.day} {et.strftime('%b')} {et.year} {str(et.hour).zfill(2)}:{str(et.minute).zfill(2)} UTC"
        if show_date:
            return f"{st.strftime('%d %b %Y')} - {et.strftime('%d %b %Y')}"
        return f"{st.strftime('%d %b %Y')} - {et.strftime('%d %b %Y')}"

    return ""


def get_time_range(
    start_time: TimestampLike,
    end_time: TimestampLike,
    freq: str | None = None,
    periods: int | None = None,
) -> pd.DatetimeIndex:
    """
    Generates a sequence of timestamps based on frequency or number of periods.

    This function either:
    - Rounds existing timestamps to the nearest interval defined by `freq`, or
    - Generates evenly spaced timestamps over a range using the specified `periods`.

    Parameters:
        freq (str, optional): A time frequency string compatible with pandas (e.g., '1H' for hourly,
            '30min' for 30-minute intervals, '1D' for daily). If provided, timestamps are rounded
            to the nearest multiple of this interval.
        periods (int, optional): The number of evenly spaced timestamps to generate. Used when
            `freq` is not provided.

    Returns:
        date_range (pandas.DatetimeIndex): A sequence of timestamps, either rounded or evenly spaced.
    """
    start_time = to_timestamp(start_time, keep_tzinfo=False)
    end_time = to_timestamp(end_time, keep_tzinfo=False)

    if not isinstance(freq, str) and not isinstance(periods, int):
        raise TypeError(
            f"{get_time_range.__name__}() missing 1 required argument: 'freq' or 'periods'"
        )
    elif isinstance(freq, str) and isinstance(periods, int):
        raise TypeError(
            f"{get_time_range.__name__}() expected 1 out of the 2 required arguments 'freq' and 'periods' but got both"
        )
    elif isinstance(freq, str):
        if freq == "MS":
            start_period = start_time.to_period("M")
            end_period = end_time.to_period("M")

            start_month = start_period.to_timestamp()
            if start_month != start_time:
                start_month = start_month + pd.Timedelta(
                    start_period.days_in_month, "D"
                )
            end_month = end_period.to_timestamp()

            n_months = int(np.round((end_month - start_month).days / 30))

            time_range = [start_month]
            for i in range(n_months):
                _period = time_range[-1].to_period("M")
                _month = time_range[-1] + pd.Timedelta(_period.days_in_month, "D")
                time_range.append(_month)
        elif freq == "SMS":
            start_period = start_time.to_period("M")
            end_period = end_time.to_period("M")

            start_month = start_period.to_timestamp()
            if start_month != start_time:
                if start_month + pd.Timedelta(14, "D") >= start_time:
                    start_month = start_month + pd.Timedelta(14, "D")
                else:
                    start_month = start_month + pd.Timedelta(
                        start_period.days_in_month, "D"
                    )
            end_month = end_period.to_timestamp()
            if end_month + pd.Timedelta(14, "D") <= end_time:
                end_month = end_month + pd.Timedelta(14, "D")

            n_semimonths = int(np.round((end_month - start_month).days / 15))

            time_range = [start_month]
            for i in range(n_semimonths):
                _ts = time_range[-1]
                if _ts.day == 15:
                    _period = time_range[-1].to_period("M")
                    _next = _period.to_timestamp() + pd.Timedelta(
                        _period.days_in_month, "D"
                    )
                else:
                    _period = time_range[-1].to_period("M")
                    _next = time_range[-1] + pd.Timedelta(14, "D")
                time_range.append(_next)
        elif "W" in freq:
            w_count = 1
            if freq[:-1] != "":
                w_count = int(freq[:-1])

            start_period = start_time.to_period("W")
            end_period = end_time.to_period("W")

            start_week = start_period.to_timestamp()
            if start_week != start_time:
                start_week = start_week + pd.Timedelta(7 * w_count, "D")
            end_week = end_period.to_timestamp()

            n_weeks = int(np.round((end_week - start_week).days / (7 * w_count)))

            time_range = [start_week]
            for i in range(n_weeks):
                _period = time_range[-1].to_period("W")
                _week = time_range[-1] + pd.Timedelta(7 * w_count, "D")
                time_range.append(_week)
        elif freq == "QS":

            def next_quarter(ts):
                q_period = pd.Timestamp(ts).to_period("Q")
                m1 = q_period.to_timestamp()
                m2 = m1 + pd.Timedelta(q_period.days_in_month, "D")
                m3 = m2 + pd.Timedelta(m2.to_period("M").days_in_month, "D")
                m4 = m3 + pd.Timedelta(m3.to_period("M").days_in_month, "D")
                return m4

            start_period = start_time.to_period("Q")
            end_period = end_time.to_period("Q")

            start_quarter = start_period.to_timestamp()
            if start_quarter != start_time:
                start_quarter = next_quarter(start_quarter)
            end_quarter = end_period.to_timestamp()

            n_quarters = int(np.round((end_quarter - start_quarter).days / 90))

            time_range = [start_quarter]
            for i in range(n_quarters):
                _quarter = next_quarter(time_range[-1])
                time_range.append(_quarter)
        elif "YS" in freq:
            y_count = 1
            if freq[:-2] != "":
                y_count = int(freq[:-2])

            start_period = start_time.to_period("Y")
            end_period = end_time.to_period("Y")

            start_year = start_period.to_timestamp()
            if start_year != start_time:
                start_year = (
                    (start_year + pd.Timedelta(366 * y_count, "D"))
                    .to_period("Y")
                    .to_timestamp()
                )
            end_year = end_period.to_timestamp()
            n_years = int(np.round((end_year - start_year).days / (365 * y_count)))

            time_range = [start_year]
            for i in range(n_years):
                _period = time_range[-1].to_period("Y")
                _year = (
                    (time_range[-1] + pd.Timedelta(366 * y_count, "D"))
                    .to_period("Y")
                    .to_timestamp()
                )
                time_range.append(_year)
        else:
            time_range = pd.date_range(
                start_time.ceil(freq), end_time.floor(freq), freq=freq
            ).to_list()
    else:
        time_range = pd.date_range(start_time, end_time, periods=periods).to_list()
    return pd.DatetimeIndex(time_range)


def lookup_value_by_timestamp(
    t: TimestampLike, times: NDArray, values: NDArray[Any]
) -> Any:
    """
    Returns the value corresponding to the timestamp closest to a given time, using interpolation.

    Parameters:
        t (TimestampLike): A single timestamp to look up.
        times (NDArray): A series of of monotonically increasing timestamps.
        values (NDArray[Any]): A series of values corresponding to each timestamp in `times`.

    Returns:
        v (Any): The value from `values` that corresponds to the closest timestamp in `times` to `t`.

    Raises:
        ValueError: If `times` and `values` have different lengths.
    """
    if t is None:
        raise ValueError(f"{lookup_value_by_timestamp.__name__}() missing `t`")
    if times is None:
        raise ValueError(f"{lookup_value_by_timestamp.__name__}() missing `times`")
    if values is None:
        raise ValueError(f"{lookup_value_by_timestamp.__name__}() missing `values`")

    t = to_timestamp(t).to_numpy()
    times = to_timestamps(times).to_numpy()
    values = np.asarray(values)

    if times.shape[0] == 0:
        raise ValueError(
            f"{lookup_value_by_timestamp.__name__}() `times` is empty but needs at least on element"
        )
    if values.shape[0] != times.shape[0]:
        raise ValueError(
            f"{lookup_value_by_timestamp.__name__}() First shapes must be the same for `values` ({values.shape[0]}) and `times` ({times.shape[0]})"
        )

    idx0 = np.searchsorted(times, t) - 1
    idx1 = np.searchsorted(times, t)

    idx0 = np.min([len(times) - 1, np.max([0, idx0])])
    idx1 = np.min([len(times) - 1, np.max([0, idx1])])

    if times[idx0] > t:
        idx0 = idx1

    total_duration = times[idx1] - times[idx0]
    duration = t - times[idx0]

    if total_duration == pd.Timedelta(0, "s"):
        frac = 0
    else:
        frac = duration / total_duration

    total_amount = values[idx1] - values[idx0]
    v = values[idx0] + total_amount * frac

    return v


@dataclass
class TimestampComparisonResult:
    is_same_year: bool
    is_same_month: bool
    is_same_day: bool
    is_same_hour: bool
    is_same_minute: bool
    is_same_second: bool

    @property
    def is_same(self) -> bool:
        return all(
            [
                self.is_same_year,
                self.is_same_month,
                self.is_same_day,
                self.is_same_hour,
                self.is_same_minute,
                self.is_same_second,
            ]
        )

    @property
    def is_same_date(self) -> bool:
        return all(
            [
                self.is_same_year,
                self.is_same_month,
                self.is_same_day,
            ]
        )

    @property
    def is_same_time(self) -> bool:
        return all(
            [
                self.is_same_hour,
                self.is_same_minute,
                self.is_same_second,
            ]
        )


def check_if_same_timestamp(
    t1: TimestampLike, t2: TimestampLike
) -> TimestampComparisonResult:
    t1 = to_timestamp(t1)
    t2 = to_timestamp(t2)

    result = TimestampComparisonResult(
        is_same_year=t1.year == t2.year,
        is_same_month=t1.month == t2.month,
        is_same_day=t1.day == t2.day,
        is_same_hour=t1.hour == t2.hour,
        is_same_minute=t1.minute == t2.minute,
        is_same_second=t1.second == t2.second,
    )

    return result


def time_to_num(
    time: NDArray | Sequence[TimestampLike],
    epoch: TimestampLike,
    format: str = "ns",
) -> NDArray:
    """
    Converts datetime-like values to numerical values relative to a given epoch.

    Args:
        time (NDArray | Iterable[TimestampLike]): Array or iterable of datetime-like values.
        epoch (TimestampLike): Reference time from which the numerical values are computed.
        format (str, optional): Time unit for conversion (e.g., "s", "ms", "us", "ns"). Defaults to "ns".

    Returns:
        NDArray: Array of floats representing the time difference from the epoch in the given unit.
    """
    time = to_timestamps(time).to_numpy()
    epoch = to_timestamp(epoch).to_numpy()
    return (time - epoch) / np.timedelta64(1, format)


def num_to_time(
    num: NDArray | Iterable,
    epoch: TimestampLike,
    format: str = "ns",
) -> NDArray:
    """
    Converts numerical time values back to datetime values relative to a given epoch.

    Args:
        num (NDArray | Iterable): Array or iterable of numeric values representing time offsets.
        epoch (TimestampLike): Reference time to which the numeric values are relative.
        format (str, optional): Time unit of the numeric values (e.g., "s", "ms", "us", "ns"). Defaults to "ns".

    Returns:
        NDArray: Array of datetime64 values corresponding to the numeric offsets from the epoch.
    """
    num = np.asarray(num)
    epoch = to_timestamp(epoch).to_numpy()
    return (num * np.timedelta64(1, format)) + epoch
