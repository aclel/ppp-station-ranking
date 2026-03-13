from .config import ScoreConfig

import pandas as pd


def rank(scores: pd.DataFrame, config: ScoreConfig):
    """Rank each window by station scores"""
    scores["rank"] = (
        scores.groupby(["window_start", "window_end"])["score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    ranked = scores.sort_values(["window_start", "rank"]).reset_index(drop=True)
    ranked.to_csv(config.output_dir / "ranking.csv", index=False)
    return ranked
