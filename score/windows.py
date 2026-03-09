from .config import ScoreConfig

import pandas as pd


def build_windows(df: pd.DataFrame, config: ScoreConfig) -> pd.DataFrame:
    """Takes a df of form (station, date, metric, value).
    Returns one row for each station, each date
    """
    default_aggregator = "median"

    if config.window_days is None:
        agg = (
            df.groupby(["station", "metric"])["value"]
            .agg(value=default_aggregator, n_days="size")
            .reset_index()
        )
        agg["window_start"] = pd.Timestamp(config.end_date)
        agg["window_end"] = pd.Timestamp(config.end_date)
        return agg[
            ["station", "window_start", "window_end", "metric", "value", "n_days"]
        ]
    else:
        raise NotImplementedError()
