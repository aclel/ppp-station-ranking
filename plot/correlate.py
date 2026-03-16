import pandas as pd
import plotly.graph_objects as go


def make_correlation_heatmap(
    ranking_df: pd.DataFrame,
    metric_cols: list[str],
    method: str = "spearman",
) -> go.Figure:
    """Build a correlation heatmap between normalised metrics"""
    corr = ranking_df[metric_cols].corr(method=method)
    n = len(ranking_df)

    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale="RdBu_r",
            text=corr.round(2).values,
            texttemplate="%{text}",
            colorbar=dict(title="ρ"),
        )
    )
    fig.update_layout(
        title=f"{method.capitalize()} correlation across stations",
        width=700,
        height=700,
        xaxis=dict(tickangle=-45),
    )
    fig.update_yaxes(autorange="reversed")
    fig.write_html("correlation.html", include_plotlyjs="cdn", full_html=True)
    return fig
