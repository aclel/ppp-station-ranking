import duckdb
import pandas as pd

PATTERN = "*rnx_pos.parquet"

# Converged when they cross 100mm
THRESH_H = 0.1
THRESH_V = 0.1


def position_sql(files: list[str], conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    if not files:
        return empty_frame()

    sql = f"""
        WITH raw AS (                                                                                                               
            SELECT                                                                                                                  
                UPPER(LEFT(regexp_extract(filename, '/([A-Z0-9]{{4}})/', 1), 4)) AS station,                                        
                CAST(datetime AS DATE)      AS day,                                                                                 
                CAST(datetime AS TIMESTAMP) AS ts,                                                                                  
                SQRT(dN*dN + dE*dE) AS errH,                                                                                        
                ABS(dU)             AS errV                                                                                         
            FROM read_parquet({files}, filename=true)
        ),                                                                                                                          
        elapsed AS (                                                                                                                
            SELECT                                                                                                                  
                station, day, errH, errV,                                                                                           
                DATEDIFF('second', MIN(ts) OVER (PARTITION BY station, day), ts) / 60.0 AS minutes_elapsed
            FROM raw                                                                                                                
        )                                                                                                                           
        SELECT                                                                                                                      
            station, day,                                                                                                           
            MIN(CASE WHEN errH < ? THEN minutes_elapsed END) AS h_conv,
            MIN(CASE WHEN errV < ? THEN minutes_elapsed END) AS v_conv                                                              
        FROM elapsed
        GROUP BY station, day                                                                                                       
        ORDER BY station, day
    """

    df = conn.execute(sql, [THRESH_H, THRESH_V]).df()

    # Fill NaNs with max epochs for the day
    max_epochs = 1440
    df[["h_conv", "v_conv"]] = df[["h_conv", "v_conv"]].fillna(max_epochs)
    return df


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["station", "day", "h_conv", "v_conv"])
