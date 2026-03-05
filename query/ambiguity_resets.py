import duckdb
import pandas as pd
from pathlib import Path

from query.base import raw_files, filter_readable, make_connection

PATTERN = "*_network_ambiguity_resets.parquet"


def build_amb_resets(
    year: int, month: int, raw_root: Path, conn: duckdb.DuckDBPyConnection
) -> pd.DataFrame:
    files = raw_files(year, month, raw_root, PATTERN)
    files = filter_readable(raw_files(year, month, raw_root, PATTERN))
    return _amb_resets_sql(files, conn)


def _amb_resets_sql(files: list[str], conn) -> pd.DataFrame:
    """Queries unique ambiguity resets on one satellite, one epoch.
    This does DISTINCT because there are likely multiple reasons
    triggered (SCDIA, MW, GF etc) for one satellite, epoch.
    """
    if not files:
        return _empty_frame()

    sql = f"""  
        WITH dedup AS (                                                                                                                        
            SELECT DISTINCT                 
                recv,                   
                CAST(datetime AS DATE)      AS day,
                CAST(datetime AS TIMESTAMP) AS epoch,                                                                                          
                UPPER(TRIM(sat))            AS sat
            FROM read_parquet({files}, union_by_name=true, hive_partitioning=false)                                                                                        
        )       
        SELECT recv AS station, day, COUNT(*) AS amb_resets                                                                                    
        FROM dedup
        GROUP BY recv, day                                                                                                                     
        ORDER BY recv, day
    """
    return conn.execute(sql).df()


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["station", "day", "amb_resets"])


conn = conn = make_connection()
df = build_amb_resets(2019, 1, Path("/data/parquet"), conn)
print(df)
