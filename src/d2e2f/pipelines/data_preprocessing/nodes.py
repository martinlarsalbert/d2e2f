import pandas as pd
from d2e2f import trips
from .prepare import prepare


def preprocess(
    df_raw: pd.DataFrame,
    renames: dict,
    do_calculate_rudder_angles=False,
) -> pd.DataFrame:
    df_ = prepare(
        df_raw=df_raw,
        do_calculate_rudder_angles=do_calculate_rudder_angles,
        renames=renames,
    )

    # To be able to save to parquet file:
    df_["time"] = df_.index.astype(str)
    df_.reset_index(inplace=True, drop=True)

    return df_


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

    df_ = trips.numbering(
        df=df_raw,
        start_number=start_number,
        trip_separator=trip_separator,
        initial_speed_separator=initial_speed_separator,
    )

    # To be able to save to parquet file:
    df_["time"] = df_.index.astype(str)
    df_.reset_index(inplace=True, drop=True)

    return df_


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
