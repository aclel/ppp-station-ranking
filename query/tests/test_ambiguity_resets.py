from pathlib import Path

from query.base import make_connection
from query.ambiguity_resets import _amb_resets_sql

TESTS_DIR = Path(__file__).parent
TOW2_FILE = str(
    TESTS_DIR
    / "data"
    / "Network_TOW200AUS_R_20190010000_01D_30S_MO_201900100_network_ambiguity_resets.parquet"
)


def test_amb_resets_one_station_one_day():
    conn = make_connection()
    df = _amb_resets_sql([TOW2_FILE], conn)

    assert len(df) == 1
    row = df.iloc[0]
    assert row["station"] == "TOW2"
    assert row["amb_resets"] >= 0

    # rough upper bound as a sanity check
    assert row["amb_resets"] < 6000
