import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from .utils import format_config_footer


def _plot_rank_by_lat_bin(ranking_df, lat_col, title, out_path, include_titles=True):
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
        title=title if include_titles else "",
        xaxis_title="Latitude bin centre (°)",
        yaxis_title="Mean rank",
    )
    if out_path:
        fig.write_html(out_path, include_plotlyjs="cdn", full_html=True)


def make_lat_ranks(
    ranking_df,
    plots_dir: Path,
    variant,
    config_label: str,
    weights: dict[str, float],
    include_titles=True,
):
    _plot_rank_by_lat_bin(
        ranking_df,
        "Latitude",
        f"Average rank by geographic latitude (20 deg bins) - {variant.upper()}<sub><br>{format_config_footer(config_label, weights)}</sub>",
        Path(plots_dir) / "lat_ranks_geographic.html",
        include_titles=include_titles,
    )


def _plot_trend_by_lat_bin(
    fits_with_lat, lat_col, title, out_path, include_titles=True
):
    bin_edges = np.arange(-90, 91, 20)
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
        title=title if include_titles else "",
        xaxis_title="Latitude bin centre (°)",
        yaxis_title="Mean slope (score / year)",
    )
    if out_path:
        fig.write_html(out_path, include_plotlyjs="cdn", full_html=True)


def make_lat_trends(
    fits: "pd.DataFrame",
    ranking_df: "pd.DataFrame",
    plots_dir: Path,
    variant,
    config_label: str,
    weights: dict[str, float],
    include_titles=True,
):
    coords = ranking_df[["station", "Latitude"]].drop_duplicates(subset="station")
    fits_with_lat = fits.merge(coords, on="station", how="inner").dropna(
        subset=["Latitude", "slope_per_year"]
    )
    _plot_trend_by_lat_bin(
        fits_with_lat,
        "Latitude",
        f"Mean score trend by geographic latitude (20 deg bins) - {variant.upper()}<sub><br>{format_config_footer(config_label, weights)}</sub>",
        Path(plots_dir) / "lat_trends_geographic.html",
        include_titles=include_titles,
    )
