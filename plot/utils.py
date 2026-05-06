import matplotlib.pyplot as plt
import pandas as pd

import plotly.graph_objects as go
import numpy as np


IGRF_CSV = "data/igrfgridData.csv"


def add_inclination_contours(fig):
    contours = inclination_contours(IGRF_CSV)
    for c in contours:
        fig.add_trace(
            go.Scattergeo(
                lon=c["lon"],
                lat=c["lat"],
                mode="lines",
                line=dict(
                    color=c["color"], width=2 if abs(c["level"]) % 20 == 0 else 1
                ),
                hoverinfo="skip",
                showlegend=False,
                opacity=0.4,
            )
        )


def inclination_contours(igrf_csv, year=2025.0):
    """Build geomagnetic inclination contours from an igrf data csv"""
    df = pd.read_csv(
        igrf_csv, comment="#", names=["date", "lat", "lon", "elev", "incl", "incl_sv"]
    )
    df = df[df["date"] == year]
    grid = (
        df.pivot_table(index="lat", columns="lon", values="incl")
        .sort_index(ascending=False)
        .sort_index(axis=1)
    )

    # Extract contour geometry froom -90 to 90 degrees every 10 degrees
    levels = range(-90, 100, 10)
    fig, ax = plt.subplots()
    cs = ax.contour(
        grid.columns.values, grid.index.values, grid.values, levels=list(levels)
    )
    plt.close(fig)

    # Flatten into a list of polylines, one entry per segment
    out = []
    for level_idx, level in enumerate(levels):
        for seg in cs.allsegs[level_idx]:
            if len(seg):
                out.append(
                    {
                        "level": level,
                        "lon": seg[:, 0],
                        "lat": seg[:, 1],
                        "color": "red"
                        if level > 0
                        else "blue"
                        if level < 0
                        else "green",
                    }
                )
    return out


def stations(stations_csv):
    stations = pd.read_csv(stations_csv)
    return stations


def add_metric_diffs(compare_df: pd.DataFrame, metric_cols: list[str]) -> pd.DataFrame:
    """Per-metric signed diff vs the relevant cluster reference.

    For the rankings's top pick in a cluster, ref is the runner-up.
    For other ranked members, ref is the user's top pick.
    Single-station clusters get NaN diffs.
    """
    df = compare_df.copy()
    df["rank_in_cluster"] = (
        df.groupby("cluster_id")["rank"].rank(method="first").astype(int)
    )
    is_best = df["rank_in_cluster"] == 1

    for m in metric_cols:
        rank1 = df.loc[df["rank_in_cluster"] == 1].set_index("cluster_id")[m]
        rank2 = df.loc[df["rank_in_cluster"] == 2].set_index("cluster_id")[m]
        ref = np.where(
            is_best,
            df["cluster_id"].map(rank2),
            df["cluster_id"].map(rank1),
        )
        df[f"{m}_diff"] = df[m] - ref
    return df
