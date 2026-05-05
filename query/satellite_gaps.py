import pandas as pd


PATTERN = "*station_observations.parquet"


def satellite_gaps_sql(files: list[str], conn) -> pd.DataFrame:
    """Queries the number of 10 minute gaps in obervations for a given satellite. Identifies stations that
    have tracking difficulties.
    """
    if not files:
        return empty_frame()

    sql = f"""  
        WITH epochs AS (
            SELECT
                UPPER(split_part(filename, '/', -2)) AS station,
                sat,
                datetime,
                MIN(elevation) AS elevation         -- same value across signals                                                                                                            
            FROM read_parquet({files}, union_by_name=true, filename=true, hive_partitioning=false)                                                                                                                  
            WHERE status = 'OBSERVED' AND elevation > 10                                                                                                                                                            
            GROUP BY station, sat, datetime                                                                                                                                                                         
        ),                                                                                                                                                                                                          
        diffs AS (      
            SELECT                                                                                                                                                                                                  
                station,
                sat,                                                                                                                                                                                                
                LAG(datetime)  OVER w AS gap_start,
                LAG(elevation) OVER w AS elev_before,
                datetime  AS gap_end,                                                                                                                                                                               
                elevation AS elev_after,
                EXTRACT(EPOCH FROM (datetime - LAG(datetime) OVER w)) / 60.0 AS gap_min                                                                                                                             
            FROM epochs                                                                                                                                                                                             
            WINDOW w AS (PARTITION BY station, sat ORDER BY datetime)
        )                                                                                                                                                                                                           
        SELECT          
            station,                                                                                                                                                                                                
            CAST(gap_start AS DATE) AS day,
            COUNT(*) AS satellite_gaps                                                                                                                                                                   
        FROM diffs                                                                                                                                                                                                  
        WHERE gap_min BETWEEN 10 and 120 -- gap at two hours                                                                                                                                                                                         
            AND elev_before >= 11        -- not in the middle of setting                                                                                                                                              
            AND elev_after  >= 11        -- not in the middle of rising
        GROUP BY station, day                                                                                                                                                                                       
        ORDER BY station, day
    """
    return conn.execute(sql).df()


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["station", "day", "satellite_gaps"])
