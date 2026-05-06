from pathlib import Path

from .rank_map import make_map
from .score_trends import make_trends
from .correlate import make_correlation_heatmap
from .igc20_map import make_agreement_map
from config import load_config

import pandas as pd
import click


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
def plot(config_path: Path) -> None:
    config = load_config(config_path)

    stations_csv = "data/igs_stations.csv"
    stations = pd.read_csv(stations_csv)
    stations["station"] = stations["Site Name"].astype(str).str[:4]

    for variant in config.variants:
        variant_dir = config.output_dir / variant.name
        ranks = pd.read_csv(variant_dir / "ranking.csv").merge(
            stations[["station", "Latitude", "Longitude"]],
            on="station",
            how="left",
        )

        metric_cols = [
            c
            for c in ranks.columns
            if c
            not in {
                "station",
                "window_start",
                "window_end",
                "score",
                "rank",
                "Latitude",
                "Longitude",
            }
        ]

        plots_dir = variant_dir
        plots_dir.mkdir(parents=True, exist_ok=True)
        make_map(ranks, metric_cols, plots_dir)
        make_trends(ranks, metric_cols, plots_dir)
        make_correlation_heatmap(ranks, metric_cols, plots_dir)
        make_agreement_map(ranks, metric_cols, plots_dir, stations)


if __name__ == "__main__":
    plot()
