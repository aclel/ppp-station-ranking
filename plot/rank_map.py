from .utils import inclination_contours

import pandas as pd
import plotly.graph_objects as go

IGRF_CSV = "data/igrfgridData.csv"


def make_map(ranking_df, metric_cols, contours=None, colorscale="viridis_r"):
    """Builds a map showing rank with colour"""
    fig = go.Figure()

    # Add geomagnetic inclination contours as a background
    contours = inclination_contours(IGRF_CSV)
    if contours:
        for c in contours:
            fig.add_trace(
                go.Scattergeo(
                    lon=c["lon"],
                    lat=c["lat"],
                    mode="lines",
                    line=dict(
                        color=c["color"], width=2 if abs(c["level"]) % 20 == 0 else 1
                    ),
                    hoverinfo="skip",
                    showlegend=False,
                    opacity=0.4,
                )
            )

    # Show stations with coloured rank, show details on hover
    fig.add_trace(
        go.Scattergeo(
            lon=ranking_df["Longitude"],
            lat=ranking_df["Latitude"],
            mode="markers",
            marker=dict(
                size=12,
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
            projection=dict(type="natural earth"),
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
        title="Station Ranks",
        title_x=0.5,  # centred
    )
    fig.write_html("ranking_map.html", include_plotlyjs="cdn", full_html=True)
    return fig
