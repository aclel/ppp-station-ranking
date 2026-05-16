from pathlib import Path
import logging

from score.data import load_metrics
from .rank_map import make_map
from .score_trends import make_trends
from .trend_fits import make_trend_fits
from .trend_map import make_trend_map
from .correlate import make_correlation_heatmap
from .igc20_map import make_agreement_map
from .lat_ranks import (
    make_lat_ranks,
    make_lat_trends,
)
from .station_map import make_station_map
from .station_metrics import make_station_metrics
from .metric_network_mean import plot_raw_network_metric
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
def plot(config_path: Path, include_titles=True) -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    log.info("Building plots")
    config = load_config(config_path)
    config_label = config_path.name

    log.info("Loading raw metrics")
    raw_df = load_metrics(config)

    igs_csv = "data/igs_stations.csv"
    stations = pd.read_csv(igs_csv)
    stations["station"] = stations["Site Name"].astype(str).str[:4]

    for variant in config.variants:
        variant_dir = config.output_dir / variant.name
        log.info(f"Building plots for {variant.name}")
        ranks = pd.read_csv(variant_dir / "ranking.csv").merge(
            stations[["station", "Latitude", "Longitude"]],
            on="station",
            how="left",
        )

        is_global = (
            ranks[["window_start", "window_end"]].drop_duplicates().shape[0] == 1
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

        log.info("Preparing plots")
        plots_dir = variant_dir
        plots_dir.mkdir(parents=True, exist_ok=True)

        log.info("Rank map")
        make_station_map(
            stations_file="data/stations.txt",
            igs_csv=igs_csv,
            plots_dir=plots_dir,
            include_titles=include_titles,
        )

        if is_global:
            log.info("Rank map")
            make_map(
                ranks,
                metric_cols,
                variant.name,
                plots_dir,
                config_label=config_label,
                weights=config.weights,
                include_titles=include_titles,
            )
            log.info("IGc20 Agreement")
            make_agreement_map(
                ranks,
                metric_cols,
                plots_dir,
                stations,
                config_label=config_label,
                weights=config.weights,
                include_titles=include_titles,
            )
            log.info("Lat ranks")
            make_lat_ranks(
                ranks,
                plots_dir,
                variant.name,
                config_label=config_label,
                weights=config.weights,
                include_titles=include_titles,
            )
            log.info("Correlations")
            make_correlation_heatmap(
                ranks,
                metric_cols,
                plots_dir,
                include_titles=include_titles,
            )
        else:
            log.info("Score trends")
            make_trends(
                ranks,
                metric_cols,
                plots_dir,
                config_label=config_label,
                weights=config.weights,
                # stations=["BRUX"],
                include_titles=include_titles,
            )
            log.info("Score trend fits")
            _, fits = make_trend_fits(
                ranks,
                plots_dir,
                config_label=config_label,
                weights=config.weights,
                include_titles=include_titles,
            )
            log.info("Score trend map")
            make_trend_map(
                fits,
                ranks,
                plots_dir,
                config_label=config_label,
                weights=config.weights,
                include_titles=include_titles,
            )
            log.info("Lat trends")
            make_lat_trends(
                fits,
                ranks,
                plots_dir,
                variant.name,
                config_label=config_label,
                weights=config.weights,
                include_titles=include_titles,
            )
            log.info("Station metrics")
            metric_stations = ["BRUX", "TOW2", "DARW"]
            for stn in metric_stations:
                make_station_metrics(
                    ranks,
                    stn,
                    metric_cols,
                    plots_dir,
                    include_titles=include_titles,
                )

            # Plot raw metrics over time for debugging
            log.info("Raw metrics")
            metric_dir = Path(plots_dir) / "raw_metrics"
            metric_dir.mkdir(parents=True, exist_ok=True)
            for metric in metric_cols:
                plot_raw_network_metric(
                    raw_df,
                    metric,
                    out_path=metric_dir / f"network_{metric}_raw.html",
                )

    log.info("Done")


if __name__ == "__main__":
    plot()
