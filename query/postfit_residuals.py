from metrics import extremes

import duckdb
import pandas as pd

PATTERN = "*_smoothed_network_residuals_smoothed.parquet"


def residuals_sql(files: list[str], conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
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
        FROM read_parquet({files})
        WHERE sigma > 0 AND postfit IS NOT NULL
    )
    SELECT               
        station, day,
        -- phase
        SQRT(
            SUM(res*res / (sigma*sigma)) FILTER (WHERE meas='PHAS_MEAS' AND res BETWEEN ? AND ?)
            / NULLIF(SUM(1.0 / (sigma*sigma)) FILTER (WHERE meas='PHAS_MEAS' AND res BETWEEN ? AND ?), 0)
        ) AS phase_wrms,
        -- code                                                                                                                                      
        SQRT(
            SUM(res*res / (sigma*sigma)) FILTER (WHERE meas='CODE_MEAS' AND res BETWEEN ? AND ?)
            / NULLIF(SUM(1.0 / (sigma*sigma)) FILTER (WHERE meas='CODE_MEAS' AND res BETWEEN ? AND ?), 0)
        ) AS code_wrms
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
            code_low,
            code_hi,
            code_low,
            code_hi,
        ],
    ).df()
    return df


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "station",
            "day",
            "phase_wrms",
            "code_wrms",
        ]
    )
