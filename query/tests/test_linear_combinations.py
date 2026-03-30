from pathlib import Path
from query.base import make_connection
from query.linear_combinations import _linear_combinations_sql

TESTS_DIR = Path(__file__).parent
TOW2_FILE = str(
    TESTS_DIR
    / "data"
    / "TOW2"
    / "TOW2_TOW200AUS_R_20190010000_01D_30S_MO_201900100_station_lc.parquet"
)


def test_linear_combinations_one_day():
    conn = make_connection()
    df = _linear_combinations_sql([TOW2_FILE], conn)
    # one (station, day)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["station"] == "TOW2"
    assert str(row["day"]) == "2019-01-01 00:00:00"

    assert 0 < row["mp1"] < 10
    assert 0 < row["mp2"] < 10
    assert 0 < row["mp5"] < 10
    assert 0 < row["mw12"] < 15
    assert 0 < row["mw15"] < 15
    assert 0 < row["mw25"] < 15
