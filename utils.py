from datetime import date
import pandas as pd


def _months_in_range(start: date, end: date) -> list[(int, int)]:
    return [
        (d.year, d.month)
        for d in pd.date_range(start, end, freq="MS", inclusive="both")
    ]
