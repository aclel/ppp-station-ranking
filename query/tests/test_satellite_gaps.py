from pathlib import Path
from query.base import make_connection
from query.satellite_gaps import satellite_gaps_sql

TESTS_DIR = Path(__file__).parent
TOW2_FILE = str(
    TESTS_DIR
    / "data"
    / "TOW2"
    / "TOW2_TOW200AUS_R_20190010000_01D_30S_MO_201900100_station_observations.parquet"
)


def test_satellite_gaps_one_day():
    conn = make_connection()
    df = satellite_gaps_sql([TOW2_FILE], conn)

    # At most one row (one station-day). Could be zero rows if TOW2 had no
    # gaps that day, then the metric is "absent" and the loader fills 0.
    assert len(df) <= 1
    if df.empty:
        return

    row = df.iloc[0]
    assert row["station"] == "TOW2"
    assert str(row["day"]) == "2019-01-01 00:00:00"
    assert row["satellite_gaps"] >= 0
