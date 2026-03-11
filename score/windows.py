from .config import ScoreConfig

import pandas as pd


def build_windows(df: pd.DataFrame, config: ScoreConfig) -> pd.DataFrame:
    """Takes a df of form (station, date, metric, value).
    Returns one row for each station, each date by taking the median value.
    """
    default_aggregator = "median"

    if config.window_days is None:
        agg = (
            df.groupby(["station", "metric"])
            .agg(
                score=("score", default_aggregator),
                n_days=("score", "size"),
                n_clipped=("clipped", "sum"),
            )
            .reset_index()
        )
        agg["window_start"] = pd.Timestamp(config.end_date)
        agg["window_end"] = pd.Timestamp(config.end_date)
        return agg[
            [
                "station",
                "window_start",
                "window_end",
                "metric",
                "score",
                "n_days",
                "n_clipped",
            ]
        ]
    else:
        raise NotImplementedError()
