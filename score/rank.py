from .config import ScoreConfig

import pandas as pd


def rank(scores: pd.DataFrame, config: ScoreConfig):
    ranked = scores.sort_values("score", ascending=False).reset_index(drop=True)
    ranked["rank"] = ranked.index + 1
    ranked.to_csv(config.output_dir / "ranking.csv", index=False)
    return ranked
