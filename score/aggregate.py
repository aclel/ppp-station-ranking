import pandas as pd


def weighted_sum(windows: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Compute weighted sum of normalised metrics over windows"""
    w = pd.Series(weights, name="weight")
    w = w / w.sum()  # renormalise to 1

    wide = windows.pivot(
        index=["station", "window_start", "window_end"],
        columns="metric",
        values="score",
    )

    # Only keep rows that have values for all columns
    wide = wide.dropna()

    # Compute additive weighted sum
    wide["score"] = (wide * w).sum(axis=1, skipna=False)
    return wide.reset_index()
