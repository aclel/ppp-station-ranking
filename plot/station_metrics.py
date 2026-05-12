from pathlib import Path

import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def make_station_metrics(
    ranking_df, station, metric_cols, plots_dir: Path, include_titles=True, cols=2
):
    """Grid of metrics over time for a single station sized for A4."""
    df = ranking_df.copy()
    df["window_start"] = pd.to_datetime(df["window_start"])
    g = df[df["station"] == station].sort_values("window_start")

    n = len(metric_cols)
    rows = -(-n // cols)  # ceiling

    fig = make_subplots(
        rows=rows,
        cols=cols,
        shared_xaxes=True,
        subplot_titles=metric_cols,
        horizontal_spacing=0.08,
        vertical_spacing=0.06,
    )

    for i, col in enumerate(metric_cols):
        r, c = i // cols + 1, i % cols + 1
        fig.add_trace(
            go.Scatter(x=g["window_start"], y=g[col], mode="lines", name=col),
            row=r,
            col=c,
        )

    fig.update_layout(
        width=794,
        height=1123,
        title=f"Metrics over time - {station}" if include_titles else None,
        showlegend=False,
        margin=dict(l=40, r=20, t=60, b=30),
        font=dict(size=9),
    )
    fig.update_annotations(font_size=10)
    fig.update_xaxes(
        tickfont=dict(size=8),
        showticklabels=True,
        dtick="M12",
        tickformat="%Y",
    )
    fig.update_yaxes(tickfont=dict(size=8))
    out_path = plots_dir / f"{station}_metrics.html"
    if out_path:
        fig.write_html(out_path)
    return fig
