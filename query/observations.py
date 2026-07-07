import pandas as pd


PATTERN = "*station_observations.parquet"


def observations_sql(files: list[str], conn) -> pd.DataFrame:
    """Queries average CN0"""
    if not files:
        return empty_frame()

    sql = f"""
        SELECT                                                                                                                      
            UPPER(LEFT(regexp_extract(filename, '/([A-Z0-9]{{4}})/', 1), 4)) AS station,                                              
            CAST(datetime AS DATE) AS day,                                                                                          
            AVG(snr) AS cn0                                                                                                    
        FROM read_parquet({files}, filename=true)
        WHERE status = 'OBSERVED'                                                                                                   
            AND elevation > 10                                                                                        
        GROUP BY station, day                                                                                                       
        ORDER BY station, day
    """
    return conn.execute(sql).df()


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["station", "day", "cn0"])
