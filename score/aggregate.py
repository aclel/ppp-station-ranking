import pandas as pd


def weighted_sum(windows: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Compute weighted sum of normalised metrics"""
    w = pd.Series(weights, name="weight")
    w = w / w.sum()  # renormalise to 1

    wide = windows.pivot(index="station", columns="metric", values="score")

    # Compute additive weighted sum
    composite = (wide * w).sum(axis=1, skipna=False)
    return pd.DataFrame({"station": composite.index, "score": composite.values})
