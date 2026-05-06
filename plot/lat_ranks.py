import numpy as np
import pandas as pd
import plotly.graph_objects as go
import aacgmv2
from datetime import datetime


def _plot_rank_by_lat_bin(ranking_df, lat_col, title, out_path):
    bin_edges = np.arange(-90, 91, 20)
    bin_labels = (bin_edges[:-1] + bin_edges[1:]) / 2

    binned = ranking_df.assign(
        _bin=pd.cut(
            ranking_df[lat_col], bins=bin_edges, labels=bin_labels, include_lowest=True
        )
    )
    avg_rank = (
        binned.groupby("_bin", observed=False)["rank"]
        .agg(mean_rank="mean", n="size")
        .reset_index()
    )

    fig = go.Figure(go.Bar(x=avg_rank["_bin"].astype(float), y=avg_rank["mean_rank"]))
    fig.update_layout(
        title=title,
        xaxis_title="Latitude bin centre (°)",
        yaxis_title="Mean rank",
    )
    fig.write_html(out_path, include_plotlyjs="cdn", full_html=True)


def make_lat_ranks(ranking_df, plots_dir):
    _plot_rank_by_lat_bin(
        ranking_df,
        "Latitude",
        "Average rank by geographic latitude (20 deg bins)",
        "lat_ranks_geographic.html",
    )


def make_mag_lat_ranks(ranking_df, plots_dir):
    epoch = datetime(2025, 1, 1)
    mlat, mlon, _ = aacgmv2.convert_latlon_arr(
        ranking_df["Latitude"].values,
        ranking_df["Longitude"].values,
        height=0.0,
        dtime=epoch,
        method_code="G2A",  # geographic -> AACGM
    )
    ranking_df["mag_lat"] = mlat

    _plot_rank_by_lat_bin(
        ranking_df,
        "mag_lat",
        "Average rank by magnetic latitude (20 deg bins)",
        "lat_ranks_magnetic.html",
    )
