import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from .utils import format_config_footer


def make_trends(
    ranking_df: pd.DataFrame,
    metric_cols: list[str],
    plots_dir: Path,
    config_label: str,
    weights: dict[str, float],
    stations=[],
    include_titles=True,
) -> go.Figure:
    """Plots station scores (not ranks) over time"""
    df = ranking_df.copy()
    df["window_start"] = pd.to_datetime(df["window_start"])
    df["window_end"] = pd.to_datetime(df["window_end"])
    df["window_mid"] = df["window_start"] + (df["window_end"] - df["window_start"]) / 2

    all_windows = df[["window_start", "window_end", "window_mid"]].drop_duplicates()
    if stations:
        df = df[df["station"].isin(stations)]

    fig = go.Figure()
    for station, sub in df.groupby("station"):
        sub = all_windows.merge(
            sub, on=["window_start", "window_end", "window_mid"], how="left"
        ).sort_values("window_mid")
        hover = sub.apply(
            lambda r: (
                ""
                if pd.isna(r["score"])
                else (
                    f"<b>{r['station']}</b><br>"
                    f"Window: {r['window_start'].date()} to {r['window_end'].date()}<br>"
                    f"Score: {r['score']:.3f}  •  Rank: {int(r['rank'])}<br>"
                    + "<br>".join(
                        f"{m}: {r[m]:.2f}" if pd.notna(r[m]) else f"{m}: -"
                        for m in metric_cols
                    )
                )
            ),
            axis=1,
        )
        fig.add_trace(
            go.Scatter(
                x=sub["window_mid"],
                y=sub["score"],
                mode="lines",
                name=station,
                hovertext=hover,
                hoverinfo="text",
                connectgaps=False,
            )
        )

    fig.update_yaxes(title="Score")
    fig.update_xaxes(title="Time")
    fig.update_layout(
        title=(
            f"Station score over time<br>{format_config_footer(config_label, weights)}"
        )
        if include_titles
        else "",
        height=700,
        legend=dict(itemsizing="constant"),
        showlegend=True,
        hovermode="x unified",
    )
    if plots_dir:
        fig.write_html(plots_dir / "score_trends.html", include_plotlyjs="cdn")
    return fig
