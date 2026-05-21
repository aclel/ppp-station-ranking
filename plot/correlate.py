from pathlib import Path

import numpy as np

import pandas as pd
import plotly.graph_objects as go


def make_correlation_heatmap(
    ranking_df: pd.DataFrame,
    metric_cols: list[str],
    plots_dir: Path,
    title: str,
    method: str = "spearman",
) -> go.Figure:
    """Build a correlation heatmap between normalised metrics"""
    corr = ranking_df[metric_cols].corr(method=method)
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr = corr.mask(mask)

    text = corr.round(2).astype(object).where(corr.notna(), "")
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale="RdBu_r",
            text=text,
            texttemplate="%{text}",
            colorbar=dict(title="ρ"),
        )
    )
    fig.update_layout(
        title=title,
        width=700,
        height=700,
        xaxis=dict(tickangle=-45),
    )
    fig.update_yaxes(autorange="reversed")
    if plots_dir:
        fig.write_html(
            plots_dir / "correlation.html", include_plotlyjs="cdn", full_html=True
        )
    return fig
