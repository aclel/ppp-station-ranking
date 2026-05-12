from .utils import add_inclination_contours, format_config_footer
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go


def make_map(
    ranking_df,
    metric_cols,
    variant: str,
    plots_dir: Path,
    config_label: str,
    weights: dict[str, float],
    include_titles=True,
    colorscale="viridis_r",
):
    """Builds a map showing rank with colour"""
    fig = go.Figure()

    add_inclination_contours(fig)

    # Show stations with coloured rank, show details on hover
    fig.add_trace(
        go.Scattergeo(
            lon=ranking_df["Longitude"],
            lat=ranking_df["Latitude"],
            mode="markers+text",
            # text=ranking_df["rank"].astype(int).astype(str),
            textposition="middle right",
            textfont=dict(size=11, color="black", weight="bold"),
            marker=dict(
                size=14,
                color=ranking_df["rank"],
                colorscale=colorscale,
                cmin=1,
                cmax=int(ranking_df["rank"].max()),
                line=dict(width=1, color="black"),
                colorbar=dict(title="Rank<br><sup>1 = best</sup>"),
            ),
            hovertext=ranking_df.apply(
                lambda r: (
                    f"<b>{r['station']}</b><br>"
                    f"Rank: {int(r['rank'])}<br>"
                    f"Score: {r['score']:.3f}<br>"
                    + "<br>".join(
                        f"{m}: {r[m]:.2f}" if pd.notna(r[m]) else f"{m}: -"
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
    )

    fig.update_layout(
        title=(
            f"Station Ranks - {variant}<br>{format_config_footer(config_label, weights)}"
        )
        if include_titles
        else "",
        title_x=0.5,  # centred
    )
    fig.write_html(
        plots_dir / "ranking_map.html", include_plotlyjs="cdn", full_html=True
    )
    return fig
