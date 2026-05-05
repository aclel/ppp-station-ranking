import time
import logging

from pathlib import Path
from .base import raw_files, filter_readable, sql_file_list
from metrics import extremes

import duckdb
import pandas as pd

log = logging.getLogger(__name__)


PATTERN = "*_smoothed_network_residuals_smoothed.parquet"


def build_residuals(
    year: int, month: int, raw_root: Path, conn: duckdb.DuckDBPyConnection
) -> pd.DataFrame:
    t0 = time.perf_counter()
    files = raw_files(year, month, raw_root, PATTERN)
    t1 = time.perf_counter()

    files = filter_readable(files)
    t2 = time.perf_counter()

    n_files = len(files)
    files = sql_file_list(files)
    if not files:
        return _empty_frame()
    t3 = time.perf_counter()

    log.info(
        "postfit_residuals %04d-%02d: glob=%.2fs readable=%.2fs sql=%.2fs files=%d",
        year,
        month,
        t1 - t0,
        t2 - t1,
        t3 - t2,
        n_files,
    )
    return _residuals_sql(files, conn)


def _residuals_sql(files: list[str], conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    phase_low, phase_hi = extremes("phase_wrms")
    code_low, code_hi = extremes("code_wrms")

    sql = f"""
    WITH considered AS (                                                                                                                           
        SELECT        
        recv AS station,                                                                                                                           
        CAST(date AS DATE) AS day,          
        meas,
        sigma,                                                                                                                                     
        CASE WHEN meas = 'PHAS_MEAS' THEN postfit * 1000.0   -- mm
            WHEN meas = 'CODE_MEAS' THEN postfit * 100.0    -- cm                                                                                 
        END AS res                          
        FROM read_parquet({files}, union_by_name=true)
        WHERE sigma > 0 AND postfit IS NOT NULL
    )
    SELECT               
        station, day,                                                                                                                                
                        
        -- phase                                                                                                                                     
        SQRT(              
        SUM(CASE WHEN meas='PHAS_MEAS' AND res BETWEEN ? AND ?
                THEN res*res / (sigma*sigma) END)
        / NULLIF(SUM(CASE WHEN meas='PHAS_MEAS' AND res BETWEEN ? AND ?
                            THEN 1.0 / (sigma*sigma) END), 0)                                                                                        
        ) AS phase_wrms,                          
        SUM(CASE WHEN meas='PHAS_MEAS' THEN 1 ELSE 0 END) AS phase_n_obs,                                                                            
        SUM(CASE WHEN meas='PHAS_MEAS' AND (res < ? OR res > ?)
                THEN 1 ELSE 0 END) AS phase_n_outliers,                                                                                             
                                                
        -- code                                                                                                                                      
        SQRT(         
        SUM(CASE WHEN meas='CODE_MEAS' AND res BETWEEN ? AND ?                                                                                     
                THEN res*res / (sigma*sigma) END)
        / NULLIF(SUM(CASE WHEN meas='CODE_MEAS' AND res BETWEEN ? AND ?                                                                            
                            THEN 1.0 / (sigma*sigma) END), 0)
        ) AS code_wrms,                                                                                                                              
        SUM(CASE WHEN meas='CODE_MEAS' THEN 1 ELSE 0 END) AS code_n_obs,
        SUM(CASE WHEN meas='CODE_MEAS' AND (res < ? OR res > ?)                                                                                      
                THEN 1 ELSE 0 END) AS code_n_outliers                                                                                                                                        
    FROM considered                                                                                                                                
    GROUP BY station, day                                                                                                                          
    ORDER BY station, day
    """

    df = conn.execute(
        sql,
        [
            phase_low,
            phase_hi,
            phase_low,
            phase_hi,
            phase_low,
            phase_hi,
            code_low,
            code_hi,
            code_low,
            code_hi,
            code_low,
            code_hi,
        ],
    ).df()
    return df


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "station",
            "day",
            "phase_wrms",
            "phase_n_obs",
            "phase_n_outliers",
            "code_wrms",
            "code_n_obs",
            "code_n_outliers",
        ]
    )
