from pathlib import Path
from query.base import make_connection
from query.observations import _observations_sql

TESTS_DIR = Path(__file__).parent
TOW2_FILE = str(
    TESTS_DIR
    / "data"
    / "TOW2"
    / "TOW2_TOW200AUS_R_20190010000_01D_30S_MO_201900100_station_observations.parquet"
)


def test_cn0_one_station_one_day():
    conn = make_connection()
    df = _observations_sql([TOW2_FILE], conn)

    # one (station, day)
    assert len(df) == 1
    row = df.iloc[0]
    assert str(row["day"]) == "2019-01-01 00:00:00"

    assert 30 < row["cn0"] < 60
