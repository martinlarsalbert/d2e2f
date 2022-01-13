"""
This is a boilerplate pipeline 'clean_thrusters_forsea'
generated using Kedro 0.17.6
"""
import pandas as pd
from kedro.io import PartitionedDataSet
import numpy as np
from typing import Union


def clean_thrusters(
    df_stat: pd.DataFrame, P_max_ratio_diff=0.3, cos_max_ratio_diff=0.3
) -> pd.DataFrame:
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

    mask = clean_mask(
        df_stat=df_stat,
        P_max_ratio_diff=P_max_ratio_diff,
        cos_max_ratio_diff=cos_max_ratio_diff,
    )
    df_select = df_stat.loc[~mask].copy()

    return df_select


def outliers_thrusters(
    df_stat: pd.DataFrame, P_max_ratio_diff=0.3, cos_max_ratio_diff=0.3
) -> pd.DataFrame:
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

    mask = clean_mask(
        df_stat=df_stat,
        P_max_ratio_diff=P_max_ratio_diff,
        cos_max_ratio_diff=cos_max_ratio_diff,
    )

    df_outliers = df_stat.loc[mask].copy()
    return df_outliers


def clean_mask(df_stat: pd.DataFrame, P_max_ratio_diff=0.3, cos_max_ratio_diff=0.3):

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
    return mask


def join_thrusters(df) -> pd.DataFrame:

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
