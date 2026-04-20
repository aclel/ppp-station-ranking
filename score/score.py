from pathlib import Path

from config import ScoreConfig
from .data import load_metrics, score_satellite_gaps, score_uptime
from .windows import build_windows
from .normalise import normalise
from .aggregate import AGGREGATORS
from .rank import rank

import pandas as pd


def run(config: ScoreConfig) -> None:
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_metrics(config)

    # Normalises between stations across entire timeseries
    # to determine global anchors for what good and bad means
    # for each metric
    scaled = normalise(df)

    # Takes the mean for each metric in each window for each station
    windows = build_windows(scaled, config)

    # Handle satellite gaps separately because they are a sum
    # Can't normalise and then take mean because it doesn't make sense
    if "satellite_gaps" in config.weights:
        gaps = score_satellite_gaps(config)
        windows = pd.concat([windows, gaps], ignore_index=True)

    if "uptime" in config.weights:
        uptime = score_uptime(config)
        windows = pd.concat([windows, uptime], ignore_index=True)

    # For each scoring variant (weighted sum, TOPSIS etc)
    for variant in config.variants:
        aggregator = AGGREGATORS[variant.aggregator]

        # Computes the weighted sum for each window at the configured weights
        scores = aggregator(windows, config.weights)

        # Ranks using the generated scores
        rank(scores, config, variant)
