from pathlib import Path


from score.config import ScoreConfig
from utils import months_in_range

import pandas as pd


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

    df = pd.concat(frames, ignore_index=True)
    return df[
        (df["date"] >= pd.Timestamp(config.start_date))
        & (df["date"] <= pd.Timestamp(config.end_date))
    ]
