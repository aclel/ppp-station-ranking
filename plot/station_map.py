from pathlib import Path
import pandas as pd
import plotly.graph_objects as go


def make_station_map(
    stations_file: Path,
    igs_csv: Path,
    plots_dir: Path,
    include_titles: bool = True,
):
    """Plot every station in stations.txt as a red circle marker."""
    codes = pd.read_csv(stations_file, header=None, names=["station"])[
        "station"
    ].str.strip()

    igs = pd.read_csv(igs_csv)
    igs["station"] = igs["Site Name"].str[:4]
    df = codes.to_frame().merge(
        igs[["station", "Latitude", "Longitude"]], on="station", how="left"
    )

    missing = df[df["Latitude"].isna()]["station"].tolist()
    if missing:
        print(f"Warning: no coords for {len(missing)} stations: {missing}")
    df = df.dropna(subset=["Latitude", "Longitude"])

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon=df["Longitude"],
            lat=df["Latitude"],
            mode="markers",
            marker=dict(
                size=8,
                color="red",
                symbol="circle",
                line=dict(width=1, color="black"),
            ),
            hovertext=df["station"],
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
        title="All Stations" if include_titles else "",
        title_x=0.5,
    )

    if plots_dir:
        fig.write_html(
            plots_dir / "station_map.html", include_plotlyjs="cdn", full_html=True
        )
    return fig
