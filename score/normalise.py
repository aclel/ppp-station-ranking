from metrics import METRICS

import numpy as np
import pandas as pd


def normalise(df: pd.DataFrame, k: float = 3.0):
    """Flips metrics to same direction, clips to k IQRS,
    and does min max scaling to [0, 1].
    """
    # Log transform metrics that are skewed like ambiguity resets (see METRICS)
    log_mask = df["metric"].map({m: META.log_transform for m, META in METRICS.items()})
    v = df["value"].astype(float)
    v = v.mask(log_mask, np.log1p(v))

    # Flip so that for all metrics higher is better
    signs = df["metric"].map(
        {m: (-1 if META.direction == "min" else 1) for m, META in METRICS.items()}
    )
    oriented = v * signs

    # Compute IQR
    g = oriented.groupby(df["metric"])
    q1 = g.transform("quantile", 0.25)
    q3 = g.transform("quantile", 0.75)
    iqr = q3 - q1

    # Determine high, low for 3 IQRs
    lo, hi = q1 - k * iqr, q3 + k * iqr
    constant = (iqr == 0) | ~np.isfinite(iqr)

    # Clip to 3 IQRs
    clipped = ((oriented < lo) | (oriented > hi)) & ~constant

    # Standardise scale to [0, 1]
    score = ((oriented.clip(lo, hi) - lo) / (hi - lo)).where(~constant, 0.5)

    return df.assign(score=score, clipped=clipped)
