import pandas as pd
import plotly.graph_objects as go


def make_trends(ranking_df: pd.DataFrame, metric_cols: list[str]) -> go.Figure:
    """Plots station scores (not ranks) over time"""
    df = ranking_df.copy()
    df["window_start"] = pd.to_datetime(df["window_start"])
    df["window_end"] = pd.to_datetime(df["window_end"])
    df["window_mid"] = df["window_start"] + (df["window_end"] - df["window_start"]) / 2

    fig = go.Figure()
    for station, sub in df.groupby("station"):
        sub = sub.sort_values("window_mid")
        hover = sub.apply(
            lambda r: (
                f"<b>{r['station']}</b><br>"
                f"Window: {r['window_start'].date()} → {r['window_end'].date()}<br>"
                f"Score: {r['score']:.3f}  •  Rank: {int(r['rank'])}<br>"
                + "<br>".join(
                    f"{m}: {r[m]:.2f}" if pd.notna(r[m]) else f"{m}: —"
                    for m in metric_cols
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
        title="Station score over time",
        height=700,
        legend=dict(itemsizing="constant"),
        hovermode="closest",
    )
    fig.write_html("score_trends.html", include_plotlyjs="cdn")
    return fig
