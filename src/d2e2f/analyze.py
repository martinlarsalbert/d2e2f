import pandas as pd
import numpy as np


def arange_trip_matrix(df: pd.DataFrame, key="sog") -> pd.DataFrame:
    """Create a trip matrix as a trip_time x trip_no data frame.

    Parameters
    ----------
    df : pd.DataFrame
        _description_
    key : str, optional
        _description_, by default "sog"

    Returns
    -------
    pd.DataFrame
        Data frame with trip time as index and trip_no as columns.
        Gaps in key value (sog) are filled with interpolation for each trip.
    """

    df_all = pd.DataFrame(
        data=0, columns=df["trip_no"].unique(), index=df["trip_time"].unique()
    )
    df_all.sort_index(inplace=True)

    for (
        trip_no,
        df_trip,
    ) in df.groupby("trip_no"):
        trip_time = df_trip["trip_time"]
        xf = df_trip[key].copy()
        xf.iloc[-1] = 0
        df_all[trip_no] = np.interp(df_all.index, trip_time, xf)

    return df_all
