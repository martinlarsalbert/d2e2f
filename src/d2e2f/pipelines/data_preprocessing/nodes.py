import pandas as pd
from kedro.io import PartitionedDataSet

from .prepare import prepare
from .trips import numbering, add_trip_columns


def slice(loaded: PartitionedDataSet, row_start=0, row_end=-1) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        new_id = partition_id.replace(".csv", ".parquet")
        partitions[new_id] = _slice(df_raw=df, row_start=row_start, row_end=row_end)

    return partitions


def _slice(df_raw: pd.DataFrame, row_start=0, row_end=-1) -> pd.DataFrame:
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
    loaded: PartitionedDataSet,
    renames: dict,
    do_calculate_rudder_angles=False,
    min_speed=0.01,
) -> PartitionedDataSet:
    partitions = {}
    for partition_id, df in loaded.items():
        # df = partition_load_func()
        try:
            partitions[partition_id] = _preprocess(
                df_raw=df,
                renames=renames,
                do_calculate_rudder_angles=do_calculate_rudder_angles,
                min_speed=min_speed,
            )
        except Exception:
            raise ValueError(f" failed on partition_id:{partition_id}")

    return partitions


def _preprocess(
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


def preprocess_trip_numbering(
    loaded: PartitionedDataSet,
    start_number: int,
    trip_separator="0 days 00:00:20",
    initial_speed_separator=0.05,
) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        partitions[partition_id] = _preprocess_trip_numbering(
            df_raw=df,
            start_number=start_number,
            trip_separator=trip_separator,
            initial_speed_separator=initial_speed_separator,
        )

    return partitions


def _preprocess_trip_numbering(
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


def preprocess_trip_columns(
    loaded: PartitionedDataSet,
) -> PartitionedDataSet:
    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        partitions[partition_id] = _preprocess_trip_columns(df=df)

    return partitions


def _preprocess_trip_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = add_trip_columns(df=df)
    return df


# def preprocess_csv_to_parquet(companies: pd.DataFrame) -> pd.DataFrame:
#    """Preprocesses the data for companies.
#
#    Args:
#        companies: Raw data.
#    Returns:
#        Preprocessed data, with `company_rating` converted to a float and
#        `iata_approved` converted to boolean.
#    """
#    companies["iata_approved"] = _is_true(companies["iata_approved"])
#    companies["company_rating"] = _parse_percentage(companies["company_rating"])
#    return companies


# def preprocess_shuttles(shuttles: pd.DataFrame) -> pd.DataFrame:
#    """Preprocesses the data for shuttles.
#
#    Args:
#        shuttles: Raw data.
#    Returns:
#        Preprocessed data, with `price` converted to a float and `d_check_complete`,
#        `moon_clearance_complete` converted to boolean.
#    """
#    shuttles["d_check_complete"] = _is_true(shuttles["d_check_complete"])
#    shuttles["moon_clearance_complete"] = _is_true(shuttles["moon_clearance_complete"])
#    shuttles["price"] = _parse_money(shuttles["price"])
#    return shuttles
#
#
# def create_model_input_table(
#    shuttles: pd.DataFrame, companies: pd.DataFrame, reviews: pd.DataFrame
# ) -> pd.DataFrame:
#    """Combines all data to create a model input table.
#
#    Args:
#        shuttles: Preprocessed data for shuttles.
#        companies: Preprocessed data for companies.
#        reviews: Raw data for reviews.
#    Returns:
#        model input table.
#
#    """
#    rated_shuttles = shuttles.merge(reviews, left_on="id", right_on="shuttle_id")
#    model_input_table = rated_shuttles.merge(
#        companies, left_on="company_id", right_on="id"
#    )
#    model_input_table = model_input_table.dropna()
#    return model_input_table
