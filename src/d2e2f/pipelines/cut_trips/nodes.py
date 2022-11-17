"""
This is a boilerplate pipeline 'cut_trips'
generated using Kedro 0.17.6
"""

import pandas as pd


def steaming(
    data_with_trip_columns: pd.DataFrame,
    min_steaming_longitude: float,
    max_steaming_longitude: float,
) -> pd.DataFrame:
    """Include only time steps when ship is steaming (excluding to/from port)
    defined beteween these two longitudes:
    min_steaming_longitude
    max_steaming_longitude

    Parameters
    ----------
    data_with_trip_columns : pd.DataFrame
        _description_
    min_steaming_longitude : float
        _description_
    max_steaming_longitude : float
        _description_

    Returns
    -------
    pd.DataFrame
        only times steps when ship is steaming (excluding to/from port)
    """

    mask = (data_with_trip_columns["longitude"] >= min_steaming_longitude) & (
        data_with_trip_columns["longitude"] <= max_steaming_longitude
    )

    data_steaming = data_with_trip_columns.loc[mask]
    return data_steaming
