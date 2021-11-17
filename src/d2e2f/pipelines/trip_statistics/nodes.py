import pandas as pd
from .trip_statistics import statistics
from .clean_statistics import clean
from kedro.io import PartitionedDataSet


def preprocess_trip_statistics(loaded: PartitionedDataSet) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        partitions[partition_id] = _preprocess_trip_statistics(df=df)

    return partitions


def _preprocess_trip_statistics(df: pd.DataFrame) -> pd.DataFrame:

    df.index = pd.to_datetime(df.index)
    df_statistics = statistics(df=df)

    df_statistics["start_time"] = df_statistics["start_time"].astype(str)
    df_statistics["end_time"] = df_statistics["end_time"].astype(str)

    return df_statistics


def preprocess_clean_statistics(
    loaded: PartitionedDataSet, min_distance=4000, min_time=700
) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        new_id = partition_id.replace(".parquet", ".csv")
        partitions[new_id] = _preprocess_clean_statistics(
            df_stat=df, min_distance=min_distance, min_time=min_time
        )

    return partitions


def _preprocess_clean_statistics(
    df_stat: pd.DataFrame, min_distance=4000, min_time=700
) -> pd.DataFrame:
    return clean(df_stat=df_stat, min_distance=min_distance, min_time=min_time)
