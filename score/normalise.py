from metrics import METRICS

import numpy as np
import pandas as pd


def normalise(df: pd.DataFrame, peer_relative=False):
    """Flips metrics to same direction, clips to 1% and 99%
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

    # For each (date, metric), subtract the network wide median.
    # Removes network wide drift (e.g. PPP product improvements)
    # so what's left is each station's deviation from its peers.
    if peer_relative:
        oriented = oriented - oriented.groupby([df["date"], df["metric"]]).transform(
            "median"
        )

    abs99 = oriented.abs().groupby(df["metric"]).transform("quantile", 0.99)
    score = (oriented / abs99).clip(-1, 1) * 0.5 + 0.5  # → [0, 1] with 0.5 = at peer

    # # Winsorise to 1% and 99%. The outliers are still kept, they're just clipped
    # # to the floor/ceiling. We don't want to remove them because we still want
    # # to know that the station is producing very large/small numbers.
    # lower_pct = 0.01
    # upper_pct = 0.99
    # g = oriented.groupby(df["metric"])
    # lo = g.transform("quantile", lower_pct)
    # hi = g.transform("quantile", upper_pct)
    # constant = (lo == hi) | ~np.isfinite(hi - lo)

    # clipped = ((oriented < lo) | (oriented > hi)) & ~constant
    # score = ((oriented.clip(lo, hi) - lo) / (hi - lo)).where(~constant, 0.5)

    return df.assign(score=score)
