from .rank_map import make_map
from .score_trends import make_trends
from .correlate import make_correlation_heatmap

import pandas as pd


def plot():
    rank_csv = "score/scenarios/results/global/ranking.csv"
    ranks = pd.read_csv(rank_csv)
    print(ranks)

    stations_csv = "data/igs_stations.csv"
    stations = pd.read_csv(stations_csv)
    stations["station"] = stations["Site Name"].astype(str).str[:4]

    ranks = ranks.merge(
        stations[["station", "Latitude", "Longitude"]], on="station", how="left"
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

    make_map(ranks, metric_cols)
    make_trends(ranks, metric_cols)
    make_correlation_heatmap(ranks, metric_cols)


if __name__ == "__main__":
    plot()
