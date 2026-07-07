import pandas as pd

PATTERN = "*_network_ambiguity_resets.parquet"


def _amb_resets_sql(files: list[str], conn, exclude_kf: bool) -> pd.DataFrame:
    """Queries unique ambiguity resets on one satellite, one epoch.
    This does DISTINCT because there are likely multiple reasons
    triggered (SCDIA, MW, GF etc) for one satellite, epoch.
    """
    if not files:
        return empty_frame()

    where_clause = "WHERE reasons != 'KF'" if exclude_kf else ""

    sql = f"""
        WITH dedup AS (
            SELECT DISTINCT
                recv,
                CAST(datetime AS DATE)      AS day,
                CAST(datetime AS TIMESTAMP) AS epoch,
                UPPER(TRIM(sat))            AS sat
            FROM read_parquet({files})
            {where_clause}
        )
        SELECT recv AS station, day, COUNT(*) AS amb_resets
        FROM dedup
        GROUP BY recv, day
        ORDER BY recv, day
    """
    return conn.execute(sql).df()


def amb_resets_sql(files: list[str], conn) -> pd.DataFrame:
    """Counts ambiguity resets for every reset reason, including KF
    (Kalman filter rejections)."""
    return _amb_resets_sql(files, conn, exclude_kf=False)


def amb_resets_no_kf_sql(files: list[str], conn) -> pd.DataFrame:
    """Counts ambiguity resets excluding resets whose only reason is KF.
    KF resets only come out of the Kalman filter, so they shouldn't be
    counted when scoring preprocessed-only metrics.
    """
    return _amb_resets_sql(files, conn, exclude_kf=True)


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["station", "day", "amb_resets"])
