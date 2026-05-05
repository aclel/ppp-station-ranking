import pandas as pd

from metrics import extremes


PATTERN = "*_station_lc.parquet"

LC_COMBOS = ("mp1", "mp2", "mp5", "mw12", "mw15", "mw25")


def linear_combinations_sql(files: list[str], conn) -> pd.DataFrame:
    """Queries RMS for each linear combination metric from the Ginan preprocessor"""
    if not files:
        return empty_frame()

    extremes_rows = ", ".join(
        f"('{c}', {extremes(c)[0]}, {extremes(c)[1]})" for c in LC_COMBOS
    )
    combo_list = ", ".join(f"'{c}'" for c in LC_COMBOS)

    sql = f"""  
        WITH bounds(combo_label, lo, hi) AS (                                                                               
            VALUES {extremes_rows}
        ),
        lc_long AS (                                                                                                        
            SELECT
                UPPER(LEFT(regexp_extract(r.filename, '/([A-Z0-9]{{4}})/', 1), 4)) AS station,                              
                CAST(r.datetime AS DATE) AS day,                                                                            
                r.combo_label,
                SQRT(AVG(r.value * r.value)) AS rms                                                                         
            FROM read_parquet({files}, union_by_name=true, filename=true, hive_partitioning=false) r                        
            JOIN bounds b USING (combo_label)
            WHERE r.value IS NOT NULL                                                                                       
            AND r.value BETWEEN b.lo AND b.hi                                                                             
            GROUP BY station, day, r.combo_label
        )                                                                                                                   
        PIVOT lc_long
        ON combo_label IN ({combo_list})                                                                                    
        USING first(rms)
        GROUP BY station, day                                                                                               
        ORDER BY station, day
    """
    return conn.execute(sql).df()


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "station",
            "day",
            "mp1",
            "mp2",
            "mw12",
            "mw15",
            "mw25",
        ]
    )
