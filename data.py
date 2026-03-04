from config import ScoreConfig
from pathlib import Path
import pandas as pd


def load_metrics(config: ScoreConfig):
    cache_dir = config.cache_dir
    convergence_cache_dir = config.convergence_cache_dir


def _read_family(cache_dir: Path, family: str, months: list[str]) -> pd.DataFrame:
    return pd.concat(
        pd.read_parquet(cache_dir / family / f"{m}.parquet") for m in months
    )


def _load_residuals(cache_dir, months, needed):
    if not needed:
        return


def _load_cn0(cache_dir, months):                                                                                                                                                                                                       
      df = _read_family(cache_dir, "cn0", months)                                                                                                                                                                                         
      return (df.rename(columns={"day": "date", "cn0_mean": "value"})                                                                                                                                                                     
                .assign(metric="cn0")
                [["station", "date", "metric", "value"]]                                                                                                                                                                                  
                .dropna(subset=["value"]))


def _load_slips(cache_dir, months):                                                                                                                                                                                                     
    df = _read_family(cache_dir, "slips", months)
    return (df.rename(columns={"day": "date", "n_resets": "value"})                                                                                                                                                                     
            .assign(metric="amb_resets")
            [["station", "date", "metric", "value"]]                                                                                                                                                                                  
            .dropna(subset=["value"]))


def load_metrics(config: ScoreConfig) -> pd.DataFrame:
    needed = set(config.weights)
    months = _months_in_range(config.start_date, config.end_date)

    frames = []
    if needed & {"phase_wrms", "code_wrms"}:
        frames.append(_load_residuals(cache_dir, months, needed))
    if "cn0" in needed:
        frames.append(_load_cn0(cache_dir, months))
    if "amb_resets" in needed:
        frames.append(_load_slips(cache_dir, months))
    if needed & {"h_conv", "v_conv"}:
        frames.append(_load_convergence(conv_cache_dir, months, needed))
    if "outage_gaps" in needed:
        frames.append(_load_outage_gaps(cache_dir, months))
    if needed & {"uptime", "active_uptime"}:
        frames.append(_load_uptime(cache_dir, months, needed))
    # mp1/mp2: figure out which family, add similarly

    df = pd.concat(frames, ignore_index=True)
    return df[(df["date"] >= cfg.start_date) & (df["date"] < cfg.end_date)]
