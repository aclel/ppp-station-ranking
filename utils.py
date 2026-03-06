from datetime import date
import pandas as pd


def months_in_range(start: date, end: date) -> list[tuple[int, int]]:
    return [
        (d.year, d.month)
        for d in pd.date_range(start, end, freq="MS", inclusive="both")
    ]


def year_months(start: date, end: date) -> list[tuple[int, int]]:
    yield from (
        f"{year:04d}-{month:02d}" for (year, month) in months_in_range(start, end)
    )
