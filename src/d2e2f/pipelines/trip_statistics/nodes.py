import pandas as pd
from .trip_statistics import statistics


def preprocess_trip_statistics(df: pd.DataFrame) -> pd.DataFrame:

    df.index = pd.to_datetime(df.index)
    df_statistics = statistics(df=df)

    df_statistics["start_time"] = df_statistics["start_time"].astype(str)
    df_statistics["end_time"] = df_statistics["end_time"].astype(str)

    return df_statistics
