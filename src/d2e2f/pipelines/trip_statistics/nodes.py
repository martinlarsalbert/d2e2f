import pandas as pd
from .trip_statistics import statistics
from .clean_statistics import clean


def preprocess_trip_statistics(df: pd.DataFrame, max_time_diff=300) -> pd.DataFrame:
    df_statistics = statistics(df=df, max_time_diff=max_time_diff)
    return df_statistics


def preprocess_clean_statistics(
    df_stat: pd.DataFrame,
    min_distance=4000,
    min_time=700,
    max_time=1400,
) -> pd.DataFrame:
    return clean(
        df_stat=df_stat, min_distance=min_distance, min_time=min_time, max_time=max_time
    )
