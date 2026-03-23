from pathlib import Path

from .config import ScoreConfig
from .data import load_metrics
from .windows import build_windows
from .normalise import normalise
from .aggregate import weighted_sum
from .rank import rank


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

    # Computes the weighted sum for each window at the configured weights
    scores = weighted_sum(windows, config.weights)

    # Ranks using the generated scores
    ranks = rank(scores, config)
