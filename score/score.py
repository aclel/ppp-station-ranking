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
    scaled = normalise(df)
    windows = build_windows(scaled, config)
    scores = weighted_sum(windows, config.weights)
    ranks = rank(scores, config)
    print(ranks)
