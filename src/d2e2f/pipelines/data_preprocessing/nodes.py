import pandas as pd
from kedro.io import PartitionedDataSet

from .prepare import prepare
import numpy as np


def join_files(partitions: dict) -> pd.DataFrame:

    df = pd.DataFrame()
    for name, partition_loader in partitions.items():
        df_ = partition_loader()
        # df_clean = df_.dropna()  # A bit dangerous...

        df = df.append(df_)

    # df = pd.concat(dfs, axis=1)

    return df


def slice(df_raw: pd.DataFrame, row_start=0, row_end=-1) -> pd.DataFrame:
    """Take a slice of the data

    Parameters
    ----------
    df_raw : pd.DataFrame
        raw data
    row_start : int, optional
        start of the slice, by default 0
    row_end : int, optional
        end of the slice, by default -1 (all)

    Returns
    -------
    pd.DataFrame
        sliced data frame

    Raises
    ------
    ValueError
        If the slice is to large an error is raised
    """

    if row_start > len(df_raw) - 1:
        raise ValueError(f"row_start={row_start} exceeds length of DataFrame")

    if row_end > len(df_raw) - 1:
        row_end = -1

    return df_raw.iloc[row_start:row_end]


def preprocess(
    df_raw: pd.DataFrame,
    renames: dict,
    P_max: float = None,
    do_calculate_rudder_angles=False,
) -> pd.DataFrame:
    df_ = prepare(
        df_raw=df_raw,
        P_max=P_max,
        do_calculate_rudder_angles=do_calculate_rudder_angles,
        renames=renames,
    )

    return df_


def numbering(
    df: pd.DataFrame,
    start_number: int = 0,
) -> pd.DataFrame:
    """Give trip numbers based on start and end in the state column

    Parameters
    ----------
    df : pd.DataFrame
        _description_
    start_number : int, optional
        number of first trip, by default 0

    Returns
    -------
    pd.DataFrame
        trip_no column added
    """

    mask = df["state"] == "start"
    starts = df.loc[mask]
    mask = df["state"] == "end"
    ends = df.loc[mask]

    # Dropping if initial end
    if ends.index[0] < starts.index[0]:
        ends.drop(index=ends.iloc[0].name, inplace=True)

    # Dropping if final start
    if ends.index[-1] < starts.index[-1]:
        starts.drop(index=starts.iloc[-1].name, inplace=True)

    # Give a trip number for each start and fill for all time steps:
    mask = df["state"] == "start"
    starts = df.loc[mask]

    start_number = 0
    end_number = start_number + 1 + len(starts)
    trip_numbers = np.arange(start_number + 1, end_number, dtype=int)

    df.loc[starts.index, "trip_no"] = trip_numbers
    df["trip_no"] = df["trip_no"].fillna(method="ffill")
    df["trip_no"] = df["trip_no"].fillna(start_number)
    df["trip_no"] = df["trip_no"].astype(int)

    return df


def find_trips(
    df: pd.DataFrame,
    min_time=800,
    min_start_speed=0.1,
) -> pd.DataFrame:
    """Find start and end of trips by analysing the speed signal

    Parameters
    ----------
    df : pd.DataFrame
        _description_
    min_time : str, optional
        Minimum trip time to dissregard false trips, by default "800S"
    min_start_speed : float, optional
        Minimum speed to start a trip, by default 0.1

    Returns
    -------
    pd.DataFrame
        dataframe with start and end events into the state column.

    """

    if isinstance(min_time, int):
        min_time = f"{min_time}S"

    # Find possible starts of trips:
    sog = df["sog"]
    mask_start = (sog < min_start_speed) & (np.roll(sog, -1) >= min_start_speed)
    df.loc[mask_start, "state"] = "start"

    # Remove false starts:
    mask = df["state"].isin(["start"])
    df["time"] = df.index
    events = df.loc[mask]
    mask = events["time"].diff() < min_time
    df.loc[events.loc[mask].index, "state"] = np.NaN

    # Calculate trip time for all trips
    mask = df["state"] == "start"
    df.loc[mask, "zero time"] = df.loc[mask, "time"]
    df["zero time"] = df["zero time"].fillna(method="ffill")
    df["trip time"] = df["time"] - df["zero time"]

    # Find end of trips:
    mask_end = (
        (np.roll(sog, 1) >= min_start_speed)
        & (sog < min_start_speed)
        & (df["trip time"] > min_time)
    )
    df.loc[mask_end, "state"] = "end"

    df.drop(columns=["zero time", "trip time"], inplace=True)

    return df
