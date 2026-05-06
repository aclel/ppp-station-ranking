from datetime import date
from pathlib import Path
import pandas as pd


def months_in_range(start: date, end: date) -> list[tuple[int, int]]:
    return [
        (d.year, d.month)
        for d in pd.date_range(start, end, freq="MS", inclusive="both")
    ]


def year_months(start: date, end: date) -> list[tuple[int, int]]:
    yield from (
        f"{year:04d}-{month:02d}" for (year, month) in months_in_range(start, end)
    )


def load_igc20_core(path: Path) -> pd.DataFrame:
    """Parse IGc20 core network.
    Columns: cluster_id (int), station (str), is_primary (bool).
    The first station on each line is the IGc20 primary.
    """
    rows = []
    cluster_id = 0
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for i, station in enumerate(line.split()):
            rows.append(
                {
                    "cluster_id": cluster_id,
                    "station": station,
                    "is_primary": i == 0,
                }
            )
        cluster_id += 1
    return pd.DataFrame(rows)
