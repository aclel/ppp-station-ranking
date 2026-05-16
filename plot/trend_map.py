from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

from .utils import add_inclination_contours, format_config_footer


def make_trend_map(
    fits: pd.DataFrame,
    ranking_df: pd.DataFrame,
    plots_dir: Path,
    config_label: str,
    weights: dict[str, float],
    include_titles=True,
) -> go.Figure:
    """Map of per-station score slope (units/year).

    Diverging colormap centred on 0: blue = improving, red = degrading.
    """
    coords = ranking_df[["station", "Latitude", "Longitude"]].drop_duplicates(
        subset="station"
    )
    df = fits.merge(coords, on="station", how="inner").dropna(
        subset=["Latitude", "Longitude", "slope_per_year"]
    )

    vmax = df["slope_per_year"].abs().quantile(0.98)

    fig = go.Figure()
    add_inclination_contours(fig)
    fig.add_trace(
        go.Scattergeo(
            lon=df["Longitude"],
            lat=df["Latitude"],
            mode="markers",
            marker=dict(
                size=14,
                color=df["slope_per_year"],
                colorscale="RdBu",
                cmin=-vmax,
                cmax=vmax,
                line=dict(width=1, color="black"),
                colorbar=dict(title="Slope<br><sup>score / year</sup>"),
            ),
            hovertext=df.apply(
                lambda r: (
                    f"<b>{r['station']}</b><br>"
                    f"slope: {r['slope_per_year']:+.4f}/yr<br>"
                    f"n windows: {int(r['n'])}"
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
        title=(
            f"Score trend per station<br>{format_config_footer(config_label, weights)}"
        )
        if include_titles
        else "",
        title_x=0.5,
    )
    if plots_dir:
        fig.write_html(
            plots_dir / "score_trend_map.html", include_plotlyjs="cdn", full_html=True
        )
    return fig
