import calendar
from datetime import date
import logging
from pathlib import Path
import os
from concurrent.futures import ThreadPoolExecutor

import duckdb
import pyarrow.parquet as pq
import pandas as pd

log = logging.getLogger(__name__)


def make_connection(
    memory_limit: str = "110GB", threads: int | None = None
) -> duckdb.DuckDBPyConnection:
    """Create an optimised DuckDB connection for aggregation."""
    conn = duckdb.connect()
    if threads is None:
        threads = os.cpu_count() or 8
    conn.execute(f"SET threads TO {threads}")
    conn.execute(f"SET memory_limit = '{memory_limit}'")
    conn.execute("SET preserve_insertion_order = false")
    conn.execute("SET enable_object_cache = true")
    return conn


def raw_files(year, month, raw_root: Path, pattern: str) -> list[str]:
    """Gives all date-dir subfolders under raw_root belonging to the given
    year and month.

    Returns a list of Paths as strings to pass on to DuckDB.
    """
    last_dom = calendar.monthrange(year, month)[1]
    out: list[str] = []
    for dom in range(1, last_dom + 1):
        day_dir = raw_root / f"{year:04d}-{month:02d}-{dom:02d}"
        out.extend(str(p) for p in day_dir.glob(f"*/{pattern}"))
    return out


def _is_readable(path: str) -> bool:
    try:
        pf = pq.ParquetFile(path)
        return pf.metadata.num_columns > 0
    except Exception:
        return False


def filter_readable(files: list[str], workers: int = 16) -> list[str]:
    """Opens each parquet file in the list and checks if they can be read."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        ok = list(ex.map(_is_readable, files))
    kept = [f for f, k in zip(files, ok) if k]
    dropped = [f for f, k in zip(files, ok) if not k]
    if dropped:
        log.warning(
            "filter_readable: dropped %d/%d (e.g. %s)",
            len(dropped),
            len(files),
            dropped[:3],
        )
    return kept


def write_month(df: pd.DataFrame, family: str, year_month: str, out_root: Path) -> Path:
    out_dir = out_root / family
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{year_month}.parquet"
    df.to_parquet(out_path, index=False)
    return out_path


def sql_file_list(files: list[str]) -> str:
    """DuckDB SQL list literal for a list of file paths."""
    inner = ", ".join(f"'{f}'" for f in files)
    return f"[{inner}]"
