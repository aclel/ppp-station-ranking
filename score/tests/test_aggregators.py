import numpy as np
import pandas as pd

from score.aggregate import weighted_sum, topsis


def _windows(values: dict[tuple[str, str], float]) -> pd.DataFrame:
    """Build a long-format windows df. Keyed by (station, metric)."""
    return pd.DataFrame(
        [
            {
                "station": s,
                "metric": m,
                "score": v,
                "window_start": pd.Timestamp("2024-01-01"),
                "window_end": pd.Timestamp("2024-01-07"),
            }
            for (s, m), v in values.items()
        ]
    )


def test_weighted_sum_equal_weights_is_mean():
    """Two metrics with equal weights -> score is the simple mean."""
    w = _windows(
        {
            ("ALIC", "a"): 0.2,
            ("ALIC", "b"): 0.8,
            ("DARW", "a"): 0.5,
            ("DARW", "b"): 0.5,
        }
    )
    out = weighted_sum(w, weights={"a": 0.5, "b": 0.5}).set_index("station")
    assert out.loc["ALIC", "score"] == 0.5  # (0.2 + 0.8) / 2
    assert out.loc["DARW", "score"] == 0.5


def test_weighted_sum_drops_stations_missing_a_metric():
    """A station without a value for every weighted metric is excluded."""
    w = _windows(
        {
            ("ALIC", "a"): 0.5,
            ("ALIC", "b"): 0.5,
            ("DARW", "a"): 0.9,  # no 'b' -- should be dropped by .dropna()
        }
    )
    out = weighted_sum(w, weights={"a": 0.5, "b": 0.5})
    assert set(out["station"]) == {"ALIC"}


def test_topsis_station_at_ideal_scores_1():
    """A station at 1.0 for every metric sits exactly on z_j+ -> closeness 1."""
    w = _windows({("ALIC", "a"): 1.0, ("ALIC", "b"): 1.0})
    out = topsis(w, weights={"a": 0.5, "b": 0.5})
    assert out.iloc[0]["score"] == 1.0


def test_topsis_station_at_anti_ideal_scores_0():
    """A station at 0.0 for every metric sits exactly on z_j- -> closeness 0."""
    w = _windows({("ALIC", "a"): 0.0, ("ALIC", "b"): 0.0})
    out = topsis(w, weights={"a": 0.5, "b": 0.5})
    assert out.iloc[0]["score"] == 0.0


def test_topsis_hand_computed():
    """Walk through by hand.

    So weighted row z_i becomes [0.5 * 0.8, 0.5 * 0.4]
    z_j+ positive ideal = [0.5, 0.5]
    z_j- negative ideal = [0, 0]

    d_pos = Distance between (0.5-0.4) and (0.5 - 0.2) = sqrt(0.1)
    d_neg = Distance between (0.4^2) and (0.2^) = sqrt(0.2)

    score = d_neg / (d_pos + d_neg) = 0.5858
    """
    #
    w = _windows({("ALIC", "a"): 0.8, ("ALIC", "b"): 0.4})
    out = topsis(w, weights={"a": 0.5, "b": 0.5})
    expected = np.sqrt(0.2) / (np.sqrt(0.1) + np.sqrt(0.2))
    assert np.isclose(out.iloc[0]["score"], expected)
