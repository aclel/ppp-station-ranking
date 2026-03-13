from datetime import date

from .config import ScoreConfig

import pandas as pd


def build_windows(df: pd.DataFrame, config: ScoreConfig) -> pd.DataFrame:
    """Takes a df of form (station, date, metric, value).
    Returns one row for each station, each window by taking the median value.
    """
    default_aggregator = "median"

    df = assign_windows(df, config.window_days, config.start_date, config.end_date)
    return (
        df.groupby(["station", "window_start", "window_end", "metric"])
        .agg(
            score=("score", default_aggregator),
            n_days=("score", "size"),
            n_clipped=("clipped", "sum"),
        )
        .reset_index()
    )


def assign_windows(
    df: pd.DataFrame, window_days: int | None, start_date: date, end_date: date
) -> pd.DataFrame:
    """Assign windows based on configured window size"""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    if window_days is None:
        df["window_start"] = pd.Timestamp(start_date)
        df["window_end"] = pd.Timestamp(end_date)
        return df

    days_since_start = (df["date"] - pd.Timestamp(start_date)).dt.days
    window_idx = days_since_start // window_days
    df["window_start"] = pd.Timestamp(start_date) + pd.to_timedelta(
        window_idx * window_days, unit="D"
    )
    df["window_end"] = df["window_start"] + pd.to_timedelta(window_days - 1, unit="D")
    return df
