from .rank_map import make_map

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

    make_map(ranks)


if __name__ == "__main__":
    plot()
