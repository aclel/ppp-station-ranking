import numpy as np
import pandas as pd
from .utils import add_inclination_contours, add_metric_diffs
from pathlib import Path
import plotly.graph_objects as go
from utils import load_igc20_core


STATUS_COLORS = {"agree": "#2ca02c", "disagree": "#d62728"}


def compare_to_igc20(igc20: pd.DataFrame, ranking: pd.DataFrame) -> pd.DataFrame:
    """Agreement between IGc20 primary and the best-ranked station in each cluster

    Drops clusters whose IGc20 primary isn't in the ranking.
    """
    merged = igc20.merge(ranking[["station", "rank"]], on="station", how="inner")

    primary = merged.loc[merged["is_primary"], ["cluster_id", "station"]].rename(
        columns={"station": "igc20_primary"}
    )
    best = merged.loc[
        merged.groupby("cluster_id")["rank"].idxmin(), ["cluster_id", "station"]
    ].rename(columns={"station": "ranking_best"})

    out = merged.merge(primary, on="cluster_id", how="inner").merge(
        best, on="cluster_id"
    )

    out["status"] = np.where(
        out["igc20_primary"] == out["ranking_best"], "agree", "disagree"
    )

    is_p = out["station"] == out["igc20_primary"]
    is_b = out["station"] == out["ranking_best"]
    out["role"] = np.select(
        [is_p & is_b, is_p, is_b],
        ["primary_and_best", "primary", "ranking_best"],
        default="other",
    )
    return out


def make_agreement_map(
    ranking_df: pd.DataFrame, metric_cols: pd.DataFrame, plots_dir: Path, stations
):
    """Map of per-cluster agreement with the IGc20 core network."""
    igc20 = load_igc20_core("data/IGc20_core.txt")
    compare_df = (
        compare_to_igc20(igc20, ranking_df)
        .merge(
            stations[["station", "Latitude", "Longitude"]],
            on="station",
            how="left",
        )
        .merge(
            ranking_df[["station", "score"] + metric_cols],
            on="station",
            how="left",
        )
    )
    # Remove clusters that only have one station
    compare_df = compare_df.groupby("cluster_id").filter(
        lambda g: g["station"].nunique() > 1
    )

    # Add metric diffs to compare between what the ranking got and the IGc
    compare_df = add_metric_diffs(compare_df, metric_cols)

    fig = go.Figure()

    # Add geomagnetic inclination contours
    add_inclination_contours(fig)

    # Draw lines from ranked station to the alternatives in the cluster
    best_loc = compare_df[
        compare_df["station"] == compare_df["ranking_best"]
    ].set_index("cluster_id")[["Latitude", "Longitude"]]

    line_lon, line_lat = [], []
    for _, r in compare_df[
        compare_df["station"] != compare_df["ranking_best"]
    ].iterrows():
        b = best_loc.loc[r["cluster_id"]]
        line_lon += [b["Longitude"], r["Longitude"], None]
        line_lat += [b["Latitude"], r["Latitude"], None]

    fig.add_trace(
        go.Scattergeo(
            lon=line_lon,
            lat=line_lat,
            mode="lines",
            line=dict(color="rgba(100,100,100,0.8)", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # Plot markers, big for the ranks we chose in red (disagree) and green (agree),
    # small for the alternatives in white
    is_ranking_best = compare_df["station"] == compare_df["ranking_best"]
    fig.add_trace(
        go.Scattergeo(
            lon=compare_df["Longitude"],
            lat=compare_df["Latitude"],
            mode="markers",
            marker=dict(
                size=np.where(is_ranking_best, 14, 7),
                color=np.where(
                    is_ranking_best,
                    compare_df["status"].map(STATUS_COLORS),
                    "white",
                ),
                line=dict(width=1.5, color="black"),
                opacity=1.0,
            ),
            hovertext=compare_df.apply(
                lambda r: (
                    f"<b>{r['station']}</b> (cluster {int(r['cluster_id'])})<br>"
                    f"Rank: {int(r['rank'])}<br>"
                    f"Score: {r['score']:.3f}<br>"
                    f"Cluster: {r['status']} "
                    f"(IGc20: {r['igc20_primary']}, Rankings: {r['ranking_best']})<br>"
                    + "<br>".join(
                        f"{m}: {r[m]:.2f} ({r[f'{m}_diff']:+.2f})"
                        if pd.notna(r[m]) and pd.notna(r[f"{m}_diff"])
                        else f"{m}: {r[m]:.2f}"
                        if pd.notna(r[m])
                        else f"{m}: -"
                        for m in metric_cols
                    )
                ),
                axis=1,
            ),
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig.update_layout(
        geo=dict(
            projection=dict(type="natural earth", rotation=dict(lon=30)),
            lonaxis=dict(range=[-150, 210]),
            showland=True,
            landcolor="rgb(243,243,243)",
            showocean=True,
            oceancolor="rgb(230,245,255)",
            showcountries=True,
            countrycolor="rgb(180,180,180)",
            coastlinecolor="rgb(100,100,100)",
        ),
        width=1200,
        height=675,
        margin=dict(l=20, r=20, t=40, b=20),
        title="Agreement with IGc20 core network<br><sub>Green = agree, Red=disagree</sub>",
        title_x=0.5,
    )

    fig.write_html(
        plots_dir / "igc20_agreement_map.html",
        include_plotlyjs="cdn",
        full_html=True,
    )
    return fig
