import pandas as pd
from .trip_statistics import statistics
from .clean_statistics import clean
from kedro.io import PartitionedDataSet
import numpy as np
from typing import Union


def preprocess_trip_statistics(loaded: PartitionedDataSet) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        partitions[partition_id] = _preprocess_trip_statistics(df=df)

    return partitions


def _preprocess_trip_statistics(df: pd.DataFrame) -> pd.DataFrame:

    # df.index = pd.to_datetime(df.index)
    df_statistics = statistics(df=df)

    # df_statistics["start_time"] = df_statistics["start_time"].astype(str)
    # df_statistics["end_time"] = df_statistics["end_time"].astype(str)

    return df_statistics


def preprocess_clean_statistics(
    loaded: PartitionedDataSet, min_distance=4000, min_time=700
) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        # new_id = partition_id.replace(".parquet", ".csv")
        new_id = partition_id
        partitions[new_id] = _preprocess_clean_statistics(
            df_stat=df, min_distance=min_distance, min_time=min_time
        )

    return partitions


def _preprocess_clean_statistics(
    df_stat: pd.DataFrame, min_distance=4000, min_time=700
) -> pd.DataFrame:
    return clean(df_stat=df_stat, min_distance=min_distance, min_time=min_time)


def clean_thrusters(
    loaded: PartitionedDataSet, P_max_ratio_diff=0.3, cos_max_ratio_diff=0.3
) -> PartitionedDataSet:
    """Remove runs where:
      * any of the thrusters have zero power.
      * (1-P_max_ratio_diff) < P1/P2 < (1-P_max_ratio_diff)
      * (1-P_max_ratio_diff) < P3/P4 < (1-P_max_ratio_diff)
      * (1-cos_max_ratio_diff) < cos_pm1/cos_pm2 < (1-cos_max_ratio_diff)
      * (1-cos_max_ratio_diff) < cos_pm3/cos_pm4 < (1-cos_max_ratio_diff)


    Parameters
    ----------
    loaded : PartitionedDataSet
        [description]
    P_max_ratio_diff=0.3, cos_max_ratio_diff=0.3 : float, optional
        [description], by default 0.3

    Returns
    -------
    PartitionedDataSet
        [description]
    """
    partitions_select = {}
    partitions_outliers = {}

    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        df_select, df_outliers = _clean_thrusters(
            df_stat=df,
            P_max_ratio_diff=P_max_ratio_diff,
            cos_max_ratio_diff=cos_max_ratio_diff,
        )
        partitions_select[partition_id] = df_select
        partitions_outliers[partition_id] = df_outliers

    return partitions_select, partitions_outliers


def _clean_thrusters(
    df_stat: pd.DataFrame, P_max_ratio_diff=0.3, cos_max_ratio_diff=0.3
) -> pd.DataFrame:

    mask1 = (
        (df_stat["P1"] == 0)
        | (df_stat["P2"] == 0)
        | (df_stat["P3"] == 0)
        | (df_stat["P4"] == 0)
    )

    P_fwd_ratio = df_stat["P1"] / df_stat["P2"]
    P_aft_ratio = df_stat["P3"] / df_stat["P4"]

    mask2 = (P_fwd_ratio.between((1 - P_max_ratio_diff), (1 + P_max_ratio_diff))) & (
        P_aft_ratio.between((1 - P_max_ratio_diff), (1 + P_max_ratio_diff))
    )

    P_fwd_ratio = df_stat["cos_pm1"] / df_stat["cos_pm2"]
    P_aft_ratio = df_stat["cos_pm3"] / df_stat["cos_pm4"]

    mask3 = P_fwd_ratio.between(
        (1 - cos_max_ratio_diff), (1 + cos_max_ratio_diff)
    ) & P_aft_ratio.between((1 - cos_max_ratio_diff), (1 + cos_max_ratio_diff))

    mask = mask1 & mask2 & mask3

    df_select = df_stat.loc[~mask].copy()
    df_outliers = df_stat.loc[mask].copy()

    return df_select, df_outliers


def join_thrusters(loaded: PartitionedDataSet) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        partitions[partition_id] = _join_thrusters(df=df)

    return partitions


def _join_thrusters(df) -> pd.DataFrame:

    df["P_fwd"] = df["P1"] + df["P2"]
    df["P_aft"] = df["P3"] + df["P4"]
    df["sin_pm_fwd"] = (df["sin_pm1"] + df["sin_pm2"]) / 2
    df["cos_pm_fwd"] = (df["cos_pm1"] + df["cos_pm2"]) / 2
    df["sin_pm_aft"] = (df["sin_pm3"] + df["sin_pm4"]) / 2
    df["cos_pm_aft"] = (df["cos_pm3"] + df["cos_pm4"]) / 2

    removes = []
    removes += [f"P{i}" for i in range(1, 5)]
    removes += [f"sin_pm{i}" for i in range(1, 5)]
    removes += [f"cos_pm{i}" for i in range(1, 5)]

    df_join = df.drop(columns=removes)
    return df_join


def train_test_split(
    loaded: PartitionedDataSet, test_ratio=0.2
) -> Union[PartitionedDataSet, PartitionedDataSet]:
    """Split the dataframe into one for training and another one for testing
    Note! The test dataset is taken from the "future" happening after the train dataset

    Parameters
    ----------
    loaded : PartitionedDataSet
        [description]
    test_ratio : float, optional
        how much of the data is used for testing?, by default 0.2

    Returns
    -------
    Union[PartitionedDataSet, PartitionedDataSet]
        partitions_train, partitions_test
    """

    partitions_train = {}
    partitions_test = {}

    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()

        df_train, df_test = _train_test_split(df=df, test_ratio=test_ratio)
        partitions_train[partition_id] = df_train
        partitions_test[partition_id] = df_test

    return partitions_train, partitions_test


def _train_test_split(
    df: pd.DataFrame, test_ratio=0.2
) -> Union[pd.DataFrame, pd.DataFrame]:

    train_index = int(np.floor((1 - test_ratio) * len(df)))
    df_train = df.iloc[0:train_index]
    df_test = df.iloc[train_index:]

    return df_train, df_test
