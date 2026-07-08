import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from .utils import format_config_footer


def _plot_rank_by_lat_bin(ranking_df, lat_col, title, out_path):
    bin_edges = np.arange(-90, 91, 30)
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
    fig.update_xaxes(tickmode="array", tickvals=bin_labels)
    if out_path:
        fig.write_html(out_path, include_plotlyjs="cdn", full_html=True)

    return fig


def make_lat_ranks(ranking_df, title, plots_dir: Path = None):
    out_path = Path(plots_dir) / "lat_ranks_geographic.html" if plots_dir else None
    return _plot_rank_by_lat_bin(
        ranking_df,
        "Latitude",
        title,
        out_path,
    )


def _plot_trend_by_lat_bin(fits_with_lat, lat_col, title, out_path):
    bin_edges = np.arange(-90, 91, 30)
    bin_labels = (bin_edges[:-1] + bin_edges[1:]) / 2

    binned = fits_with_lat.assign(
        _bin=pd.cut(
            fits_with_lat[lat_col],
            bins=bin_edges,
            labels=bin_labels,
            include_lowest=True,
        )
    )
    avg_slope = (
        binned.groupby("_bin", observed=False)["slope_per_year"]
        .agg(mean_slope="mean", n="size")
        .reset_index()
    )

    fig = go.Figure(
        go.Bar(
            x=avg_slope["_bin"].astype(float),
            y=avg_slope["mean_slope"],
            marker_color=avg_slope["mean_slope"].apply(
                lambda v: "steelblue" if v >= 0 else "tomato"
            ),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Latitude bin centre (°)",
        yaxis_title="Mean slope (score / year)",
    )
    fig.update_xaxes(tickmode="array", tickvals=bin_labels)
    if out_path:
        fig.write_html(out_path, include_plotlyjs="cdn", full_html=True)
    return fig


def make_lat_trends(
    fits: "pd.DataFrame", ranking_df: "pd.DataFrame", title: str, plots_dir: Path = None
):
    out_path = Path(plots_dir) / "lat_trends_geographic.html" if plots_dir else None
    coords = ranking_df[["station", "Latitude"]].drop_duplicates(subset="station")
    fits_with_lat = fits.merge(coords, on="station", how="inner").dropna(
        subset=["Latitude", "slope_per_year"]
    )
    return _plot_trend_by_lat_bin(fits_with_lat, "Latitude", title, out_path)
