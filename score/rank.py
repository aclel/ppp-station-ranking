from config import ScoreConfig, Variant

import pandas as pd


def rank(scores: pd.DataFrame, config: ScoreConfig, variant: Variant):
    """Rank each window by station scores"""
    scores["rank"] = (
        scores.groupby(["window_start", "window_end"])["score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    ranked = scores.sort_values(["window_start", "rank"]).reset_index(drop=True)
    variant_dir = config.output_dir / variant.name
    variant_dir.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(variant_dir / "ranking.csv", index=False)
    return ranked
