import plotly.graph_objects as go
import pandas as pd

from metrics import METRICS


def plot_raw_network_metric(raw_df, metric, out_path=None):
    """Daily network mean for a single metric in raw units.

    Expects long form data with columns (station, date, metric, value)
    as returned by score.data.load_metrics.
    """
    df = raw_df[raw_df["metric"] == metric].copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["value"])

    lo, hi = df["value"].quantile([0.01, 0.99])
    df = df[df["value"].between(lo, hi)]

    agg = df.groupby("date")["value"].mean().reset_index(name="mean")

    units = METRICS[metric].units
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=agg["date"],
            y=agg["mean"],
            mode="lines",
            line=dict(color="crimson", width=1.5),
            name="mean",
            hovertemplate=f"%{{x|%Y-%m-%d}}<br>mean: %{{y:.3f}} {units}<extra></extra>",
        )
    )
    fig.update_layout(
        title=f"Network {metric} - mean (raw)",
        xaxis_title="date",
        yaxis_title=f"{metric} ({units})",
        width=794,
        height=500,
        margin=dict(l=40, r=20, t=60, b=40),
        hovermode="x unified",
    )
    fig.update_xaxes(dtick="M12", tickformat="%Y", hoverformat="%Y-%m-%d")
    if out_path:
        fig.write_html(out_path)
    return fig
