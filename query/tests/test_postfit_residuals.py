from pathlib import Path
from query.base import make_connection
from query.postfit_residuals import _residuals_sql

TESTS_DIR = Path(__file__).parent
TOW2_FILE = str(
    TESTS_DIR
    / "data"
    / "TOW2"
    / "Network_TOW200AUS_R_20190010000_01D_30S_MO_201900100_smoothed_network_residuals_smoothed.parquet"
)


def test_residuals_one_station_one_day():
    conn = make_connection()
    df = _residuals_sql([TOW2_FILE], conn)

    # one (station, day)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["station"] == "TOW2"
    assert str(row["day"]) == "2019-01-01 00:00:00"

    # phase_wrms in mm: healthy station should be 1–5 mm
    assert -10 < row["phase_wrms"] < 10.0

    # code_wrms in cm: healthy station should be 5–50 cm
    assert -100 < row["code_wrms"] < 100.0
