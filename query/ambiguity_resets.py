import pandas as pd

PATTERN = "*_network_ambiguity_resets.parquet"


def amb_resets_sql(files: list[str], conn) -> pd.DataFrame:
    """Queries unique ambiguity resets on one satellite, one epoch.
    This does DISTINCT because there are likely multiple reasons
    triggered (SCDIA, MW, GF etc) for one satellite, epoch.
    """
    if not files:
        return empty_frame()

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


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["station", "day", "amb_resets"])
