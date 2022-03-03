import pandas as pd


def clean(
    df_stat: pd.DataFrame, min_distance=4000, min_time=700, max_time=1400
) -> pd.DataFrame:
    """Clean the statistics, removing outliers with unrealistic trip times.

    min_trip_time : float
        minimum realistic trip time

    Returns:
        pd.DataFrame: [description]
    """

    mask = (df_stat["distance"] > min_distance) & (
        df_stat["distance"] < df_stat["distance"].quantile(0.99)
    )
    df_cleaned = df_stat.loc[mask].copy()

    mask = (df_cleaned["trip_time"] > min_time) & (df_cleaned["trip_time"] < max_time)
    df_cleaned = df_cleaned.loc[mask].copy()

    return df_cleaned
