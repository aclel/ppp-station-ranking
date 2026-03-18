import duckdb
import pandas as pd
from pathlib import Path

from metrics import extremes
from query.base import raw_files, filter_readable, sql_file_list

PATTERN = "*station_observations.parquet"


def build_observations(
    year: int, month: int, raw_root: Path, conn: duckdb.DuckDBPyConnection
) -> pd.DataFrame:
    files = raw_files(year, month, raw_root, PATTERN)
    files = filter_readable(files)
    files = sql_file_list(files)
    return _observations_sql(files, conn)


def _observations_sql(files: list[str], conn) -> pd.DataFrame:
    """Queries average CN0"""
    if not files:
        return _empty_frame()

    cn0_low, cn0_hi = extremes("cn0")

    sql = f"""  
        SELECT                                                                                                                      
            UPPER(LEFT(regexp_extract(filename, '/([A-Z0-9]{{4}})/', 1), 4)) AS station,                                              
            CAST(datetime AS DATE) AS day,                                                                                          
            AVG(snr) AS cn0                                                                                                    
        FROM read_parquet({files}, union_by_name=true, filename=true, hive_partitioning=false)                                         
        WHERE status = 'OBSERVED'                                                                                                   
            AND elevation > 10                                                                                                        
            AND snr IS NOT NULL
            AND snr BETWEEN ? AND ?                                                                                                     
        GROUP BY station, day                                                                                                       
        ORDER BY station, day
    """
    return conn.execute(sql, [cn0_low, cn0_hi]).df()


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["station", "day", "cn0"])
