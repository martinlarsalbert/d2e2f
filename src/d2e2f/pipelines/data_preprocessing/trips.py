import pandas as pd
import numpy as np


# def numbering(
#    df: pd.DataFrame,
#    start_number: int,
#    harbours: dict,
#    trip_separator="0 days 00:00:20",
#    initial_speed_separator=0.05,
# ) -> pd.DataFrame:
#    """Add a trip number to each row in df
#
#    Parameters
#    ----------
#    df : pd.DataFrame
#        data (all data or partition of data)
#    start_number :
#        start of the numbering (not 0 if this is not the first dask partion)
#    trip_separator : str, optional
#        Time windows in the dataframe exceeding this time will divide the trips, by default '0 days 00:00:20'
#    initial_speed_separator : float
#        if the initial speed is lower than this, this is considered as a trip start also.
#
#    Returns
#
#    Returns
#    -------
#    pd.DataFrame
#        df
#    """
#
#    df_starts = get_starts(
#        df=df,
#        trip_separator=trip_separator,
#        initial_speed_separator=initial_speed_separator,
#    )
#
#    end_number = start_number + 1 + len(df_starts)
#    trip_numbers = np.arange(start_number + 1, end_number, dtype=int)
#
#    if "trip_no" in df:
#        df["trip_no"] = None
#
#    df.loc[df_starts.index, "trip_no"] = trip_numbers
#    df["trip_no"] = df["trip_no"].fillna(method="ffill")
#    df["trip_no"] = df["trip_no"].fillna(start_number)
#    df["trip_no"] = df["trip_no"].astype(int)
#
#    return df
#
#
# def get_starts(
#    df: pd.DataFrame,
#    trip_separator="0 days 00:01:00",
#    separator_max_speed=1.0,
#    initial_speed_separator=0.05,
# ) -> pd.DataFrame:
#    """get start and end of complete trips from df.
#
#    Parameters
#    ----------
#    df : pd.DataFrame
#        Time series for all trips
#    trip_separator : str, optional
#        Time windows in the dataframe exceeding this time will divide the trips, by default '0 days 00:00:20'
#    initial_speed_separator : float
#        if the initial speed is lower than this, this is considered as a trip start also.
#
#    Returns
#    -------
#    (pd.DataFrame, pd.DataFrame)
#        df_starts,df_ends
#        dataframes with rows from df with starts and ends.
#    """
#
#    df.sort_index(inplace=True)
#    mask = df.index.to_series().diff() > trip_separator
#
#    ## First part can be a begining of a trip:
#    if df.iloc[0]["sog"] < initial_speed_separator:
#        mask[0] = True
#
#    df_starts = df.loc[mask]
#
#    ## Also checking that the speed is low enough at the start:
#    mask = df_starts["sog"] < separator_max_speed
#    df_starts = df_starts.loc[mask]
#
#    return df_starts.copy()
#
