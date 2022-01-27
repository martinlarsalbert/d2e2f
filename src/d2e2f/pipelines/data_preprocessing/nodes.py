import pandas as pd
from kedro.io import PartitionedDataSet

from .prepare import prepare
from .trips import numbering, add_trip_columns


def join_files(partitions: dict) -> pd.DataFrame:

    df = pd.DataFrame()
    for name, partition_loader in partitions.items():
        df_ = partition_loader()
        # df_clean = df_.dropna()  # A bit dangerous...

        df = df.append(df_)

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


# def preprocess(
#    loaded: PartitionedDataSet,
#    renames: dict,
#    do_calculate_rudder_angles=False,
#    min_speed=0.01,
# ) -> PartitionedDataSet:
#    partitions = {}
#    for partition_id, df in loaded.items():
#        # df = partition_load_func()
#        try:
#            partitions[partition_id] = _preprocess(
#                df_raw=df,
#                renames=renames,
#                do_calculate_rudder_angles=do_calculate_rudder_angles,
#                min_speed=min_speed,
#            )
#        except Exception:
#            raise ValueError(f" failed on partition_id:{partition_id}")
#
#    return partitions


def preprocess(
    df_raw: pd.DataFrame,
    renames: dict,
    do_calculate_rudder_angles=False,
    min_speed=0.01,
) -> pd.DataFrame:
    df_ = prepare(
        df_raw=df_raw,
        do_calculate_rudder_angles=do_calculate_rudder_angles,
        renames=renames,
        min_speed=min_speed,
    )

    return df_


# def preprocess_trip_numbering(
#    loaded: PartitionedDataSet,
#    start_number: int,
#    trip_separator="0 days 00:00:20",
#    initial_speed_separator=0.05,
# ) -> PartitionedDataSet:
#    partitions = {}
#    for partition_id, partition_load_func in loaded.items():
#        df = partition_load_func()
#        partitions[partition_id] = _preprocess_trip_numbering(
#            df_raw=df,
#            start_number=start_number,
#            trip_separator=trip_separator,
#            initial_speed_separator=initial_speed_separator,
#        )
#
#    return partitions


def preprocess_trip_numbering(
    df_raw: pd.DataFrame,
    start_number: int,
    trip_separator="0 days 00:00:20",
    initial_speed_separator=0.05,
) -> pd.DataFrame:
    #    """Preprocesses the data adding trip numbers.
    #    """

    df_raw.index = pd.to_datetime(df_raw.index)
    df_raw.sort_index(inplace=True)

    df_ = numbering(
        df=df_raw,
        start_number=start_number,
        trip_separator=trip_separator,
        initial_speed_separator=initial_speed_separator,
    )

    return df_


# def preprocess_trip_columns(
#    loaded: PartitionedDataSet,
# ) -> PartitionedDataSet:
#    partitions = {}
#    for partition_id, partition_load_func in loaded.items():
#        df = partition_load_func()
#        partitions[partition_id] = _preprocess_trip_columns(df=df)
#
#    return partitions


def preprocess_trip_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = add_trip_columns(df=df)
    return df
