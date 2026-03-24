from pathlib import Path
from query.base import make_connection
from query.position import _position_sql

TESTS_DIR = Path(__file__).parent
TOW2_FILE = str(
    TESTS_DIR / "data" / "TOW2" / "TOW200AUS_R_20190010000_01D_30S_MO.rnx_pos.parquet"
)


def test_convergence_time():
    conn = make_connection()
    df = _position_sql([TOW2_FILE], conn)

    # one (station, day)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["station"] == "TOW2"
    assert str(row["day"]) == "2019-01-01 00:00:00"

    assert 0 < row["h_conv"] < 60
    assert 0 < row["v_conv"] < 60
