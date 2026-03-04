from pathlib import Path
import pytest
from query.base import make_connection
from query.postfit_residuals import _residuals_sql
from metrics import thresholds

TOW2_FILE = "/data/parquet/2019-01-01/TOW2/Network_TOW200AUS_R_20190010000_01D_30S_MO_201900100_smoothed_network_residuals_smoothed.parquet"


def test_residuals_one_station_one_day():
    conn = make_connection()
    df = _residuals_sql([TOW2_FILE], conn)

    # one (station, day)
    assert len(df) == 1
    row = df.iloc[0]
    assert row["station"] == "TOW2"
    assert str(row["date"]) == "2019-01-01"

    # phase_wrms in mm: healthy station should be 1–5 mm
    assert -10 < row["phase_wrms"] < 10.0

    # code_wrms in cm: healthy station should be 5–50 cm
    assert -100 < row["code_wrms"] < 100.0

    # Check all rows are considered
    assert row["phase_n_obs"] == 86255
    assert row["code_n_obs"] == 86255

    # outlier rate sanity: less than 1% for a healthy station
    assert 0 <= row["phase_n_outliers"] / row["phase_n_obs"] < 0.01
    assert 0 <= row["code_n_outliers"] / row["code_n_obs"] < 0.01
