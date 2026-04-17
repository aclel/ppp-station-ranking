import pandas as pd
import numpy as np


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


def topsis(windows: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """TOPSIS closeness score per window.

    Inputs are already oriented (higher = better) and min-max scaled to 0,1
    via normalise, so we skip TOPSIS vector normalisation step and treat
    1.0 as the absolute ideal and 0.0 as the absolute anti-ideal.
    """
    w = pd.Series(weights, name="weight")
    w = w / w.sum()

    Z = windows.pivot(
        index=["station", "window_start", "window_end"],
        columns="metric",
        values="score",
    ).dropna()

    # Align weights to the metric columns actually present, in column order
    w = w.reindex(Z.columns)

    # Weighted normalised values: z_ij = w_j * (raw normalised value)
    z = Z.to_numpy() * w.to_numpy()

    # Absolute ideals positive and negative: (z_j+ and z_j-)
    z_pos = w.to_numpy()
    z_neg = np.zeros_like(z_pos)

    # Euclidean distance per row to each ideal
    d_pos = np.sqrt(((z_pos - z) ** 2).sum(axis=1))
    d_neg = np.sqrt(((z_neg - z) ** 2).sum(axis=1))

    # Relative closeness in (0,1), 1 = at ideal best
    closeness = d_neg / (d_pos + d_neg)

    Z["score"] = closeness
    return Z.reset_index()


AGGREGATORS = {
    "weighted_sum": weighted_sum,
    "topsis": topsis,
}
