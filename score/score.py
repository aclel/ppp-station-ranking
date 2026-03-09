from pathlib import Path

from .config import ScoreConfig
from .data import load_metrics
from .windows import build_windows


def run(config: ScoreConfig) -> None:
    out_dir = Path(config.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = load_metrics(config)
    windows = build_windows(df, config)
    print(windows)
