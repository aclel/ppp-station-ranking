from pathlib import Path

from query.base import make_connection
from query.ambiguity_resets import amb_resets_sql, amb_resets_no_kf_sql

TESTS_DIR = Path(__file__).parent
TOW2_FILE = str(
    TESTS_DIR
    / "data"
    / "TOW2"
    / "Network_TOW200AUS_R_20190010000_01D_30S_MO_201900100_network_ambiguity_resets.parquet"
)


def test_amb_resets_one_station_one_day():
    conn = make_connection()
    df = amb_resets_sql([TOW2_FILE], conn)

    assert len(df) == 1
    row = df.iloc[0]
    assert row["station"] == "TOW2"
    assert row["amb_resets"] >= 0

    # rough upper bound as a sanity check
    assert row["amb_resets"] < 6000


def test_amb_resets_no_kf_excludes_kf_only_resets():
    conn = make_connection()
    all_reasons = amb_resets_sql([TOW2_FILE], conn)
    no_kf = amb_resets_no_kf_sql([TOW2_FILE], conn)

    assert len(no_kf) == 1
    row = no_kf.iloc[0]
    assert row["station"] == "TOW2"

    # Resets that are only triggered by KF should be dropped, so the
    # no-KF count must be strictly lower than the all-reasons count.
    assert row["amb_resets"] < all_reasons.iloc[0]["amb_resets"]
