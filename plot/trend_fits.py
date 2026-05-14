import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from .utils import format_config_footer


def make_trend_fits(
    ranking_df: pd.DataFrame,
    plots_dir: Path,
    config_label: str,
    weights: dict[str, float],
    stations=[],
    include_titles=True,
) -> tuple[go.Figure, pd.DataFrame]:
    """Per-station linear fit of score over time.

    Returns the figure and a DataFrame of fits (station, slope_per_year,
    intercept, n) sorted by slope. Also writes html + csv to plots_dir.
    """
    df = ranking_df.copy()
    df["window_start"] = pd.to_datetime(df["window_start"])
    df["window_end"] = pd.to_datetime(df["window_end"])
    df["window_mid"] = df["window_start"] + (df["window_end"] - df["window_start"]) / 2
    if stations:
        df = df[df["station"].isin(stations)]

    t0 = df["window_mid"].min()
    df["t_days"] = (df["window_mid"] - t0).dt.total_seconds() / 86400

    rows = []
    fig = go.Figure()
    for station, sub in df.groupby("station"):
        sub = sub.sort_values("window_mid").dropna(subset=["score"])
        if len(sub) < 2:
            continue
        slope, intercept = np.polyfit(sub["t_days"], sub["score"], 1)
        yhat = slope * sub["t_days"] + intercept
        rows.append(
            {
                "station": station,
                "slope_per_year": slope * 365,
                "intercept": intercept,
                "n": len(sub),
            }
        )
        fig.add_trace(
            go.Scatter(
                x=sub["window_mid"],
                y=yhat,
                mode="lines",
                name=f"{station} ({slope * 365:+.3f}/yr)",
                hovertemplate=(
                    f"<b>{station}</b><br>%{{x|%Y-%m-%d}}<br>fit: %{{y:.3f}}<extra></extra>"
                ),
            )
        )

    fits = pd.DataFrame(rows).sort_values("slope_per_year", ascending=False)
    fits.to_csv(plots_dir / "score_trend_fits.csv", index=False)

    fig.update_yaxes(title="Score (linear fit)")
    fig.update_xaxes(title="Time")
    fig.update_layout(
        title=(
            f"Score linear trend per station<br>{format_config_footer(config_label, weights)}"
        )
        if include_titles
        else "",
        height=700,
        legend=dict(itemsizing="constant"),
        showlegend=True,
        hovermode="x unified",
    )
    fig.write_html(plots_dir / "score_trend_fits.html", include_plotlyjs="cdn")
    return fig, fits
