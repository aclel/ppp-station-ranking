"""These functions are used to load data from the query cache
that was built with the query module.
"""

from pathlib import Path


from score.config import ScoreConfig
from utils import months_in_range
from .windows import assign_windows

import pandas as pd
import numpy as np


def _read_family(cache_dir: Path, family: str, year_months: list[str]) -> pd.DataFrame:
    return pd.concat(
        pd.read_parquet(cache_dir / family / f"{year_month}.parquet")
        for year_month in year_months
    )


def _load_postfit_residuals(cache_dir, months, needed) -> pd.DataFrame:
    df = _read_family(cache_dir, "postfit_residuals", months).rename(
        columns={"day": "date"}
    )
    cols = [c for c in ("phase_wrms", "code_wrms") if c in needed]
    return df.melt(
        id_vars=["station", "date"],
        value_vars=cols,
        var_name="metric",
        value_name="value",
    ).dropna(subset=["value"])


def _load_amb_resets(cache_dir, months) -> pd.DataFrame:
    df = _read_family(cache_dir, "amb_resets", months).rename(
        columns={"day": "date", "amb_resets": "value"}
    )
    df["metric"] = "amb_resets"
    return df[["station", "date", "metric", "value"]].dropna(subset=["value"])


def _load_observations(cache_dir, months) -> pd.DataFrame:
    df = _read_family(cache_dir, "observations", months).rename(
        columns={"day": "date", "cn0": "value"}
    )
    df["metric"] = "cn0"
    return df[["station", "date", "metric", "value"]].dropna(subset=["value"])


def _load_position(cache_dir, months, needed) -> pd.DataFrame:
    df = _read_family(cache_dir, "position", months).rename(columns={"day": "date"})
    cols = [c for c in ("h_conv", "v_conv") if c in needed]
    return df.melt(
        id_vars=["station", "date"],
        value_vars=cols,
        var_name="metric",
        value_name="value",
    ).dropna(subset=["value"])


LC_NAMES = ("mp1", "mp2", "mp5", "mw12", "mw15", "mw25")


def _load_linear_combinations(cache_dir, months, needed) -> pd.DataFrame:
    df = _read_family(cache_dir, "linear_combinations", months).rename(
        columns={"day": "date"}
    )
    cols = [c for c in LC_NAMES if c in needed]
    return df.melt(
        id_vars=["station", "date"],
        value_vars=cols,
        var_name="metric",
        value_name="value",
    ).dropna(subset=["value"])


def score_satellite_gaps(config) -> pd.DataFrame:
    months = [
        f"{y:04d}-{m:02d}"
        for y, m in months_in_range(config.start_date, config.end_date)
    ]
    df = _read_family(config.cache_dir, "satellite_gaps", months).rename(
        columns={"day": "date"}
    )
    df["date"] = pd.to_datetime(df["date"])
    df = df[
        (df["date"] >= pd.Timestamp(config.start_date))
        & (df["date"] <= pd.Timestamp(config.end_date))
    ]

    df = assign_windows(df, config.window_days, config.start_date, config.end_date)

    sums = (
        df.groupby(["station", "window_start", "window_end"])["satellite_gaps"]
        .sum()
        .reset_index()
    )
    print(sums)

    v = np.log1p(sums["satellite_gaps"].clip(lower=0))
    if v.max() > v.min():
        sums["score"] = 1.0 - (v - v.min()) / (v.max() - v.min())
    else:
        sums["score"] = 0.5

    sums["metric"] = "satellite_gaps"
    return sums[["station", "window_start", "window_end", "metric", "score"]]


def load_metrics(config: ScoreConfig) -> pd.DataFrame:
    needed = set(config.weights)
    months = [
        f"{y:04d}-{m:02d}"
        for y, m in months_in_range(config.start_date, config.end_date)
    ]

    frames = []
    if needed & {"phase_wrms", "code_wrms"}:
        frames.append(_load_postfit_residuals(config.cache_dir, months, needed))
    if "amb_resets" in needed:
        frames.append(_load_amb_resets(config.cache_dir, months))
    if "cn0" in needed:
        frames.append(_load_observations(config.cache_dir, months))
    if needed & {"h_conv", "v_conv"}:
        frames.append(_load_position(config.cache_dir, months, needed))
    if needed & set(LC_NAMES):
        frames.append(_load_linear_combinations(config.cache_dir, months, needed))

    df = pd.concat(frames, ignore_index=True)
    return df[
        (df["date"] >= pd.Timestamp(config.start_date))
        & (df["date"] <= pd.Timestamp(config.end_date))
    ]
