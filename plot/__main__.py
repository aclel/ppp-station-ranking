from pathlib import Path
import logging

from .rank_map import make_map
from .score_trends import make_trends
from .correlate import make_correlation_heatmap
from .igc20_map import make_agreement_map
from .lat_ranks import make_lat_ranks, make_mag_lat_ranks
from config import load_config

import pandas as pd
import click

log = logging.getLogger("plot")


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
def plot(config_path: Path) -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    log.info("Building plots")
    config = load_config(config_path)
    config_label = config_path.name

    stations_csv = "data/igs_stations.csv"
    stations = pd.read_csv(stations_csv)
    stations["station"] = stations["Site Name"].astype(str).str[:4]

    for variant in config.variants:
        variant_dir = config.output_dir / variant.name
        log.info(f"Building plots for {variant.name}")
        ranks = pd.read_csv(variant_dir / "ranking.csv").merge(
            stations[["station", "Latitude", "Longitude"]],
            on="station",
            how="left",
        )

        log.info("Building metric cols")
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
        metric_cols.sort(
            key=lambda m: config.weights.get(m, float("-inf")), reverse=True
        )

        plots_dir = variant_dir
        plots_dir.mkdir(parents=True, exist_ok=True)
        make_map(
            ranks,
            metric_cols,
            variant.name,
            plots_dir,
            config_label=config_label,
            weights=config.weights,
        )
        make_trends(
            ranks,
            metric_cols,
            plots_dir,
            config_label=config_label,
            weights=config.weights,
        )
        make_correlation_heatmap(
            ranks,
            metric_cols,
            plots_dir,
        )
        make_agreement_map(
            ranks,
            metric_cols,
            plots_dir,
            stations,
            config_label=config_label,
            weights=config.weights,
        )
        make_lat_ranks(
            ranks,
            plots_dir,
        )
        make_mag_lat_ranks(ranks, plots_dir)


if __name__ == "__main__":
    plot()
