import pandas as pd
import numpy as np


def numbering(
    df: pd.DataFrame,
    start_number: int,
    trip_separator="0 days 00:00:20",
    initial_speed_separator=0.05,
) -> pd.DataFrame:
    """Add a trip number to each row in df

    Parameters
    ----------
    df : pd.DataFrame
        data (all data or partition of data)
    start_number :
        start of the numbering (not 0 if this is not the first dask partion)
    trip_separator : str, optional
        Time windows in the dataframe exceeding this time will divide the trips, by default '0 days 00:00:20'
    initial_speed_separator : float
        if the initial speed is lower than this, this is considered as a trip start also.

    Returns

    Returns
    -------
    pd.DataFrame
        df
    """

    df_starts = get_starts(
        df=df,
        trip_separator=trip_separator,
        initial_speed_separator=initial_speed_separator,
    )

    end_number = start_number + 1 + len(df_starts)
    trip_numbers = np.arange(start_number + 1, end_number, dtype=int)

    if "trip_no" in df:
        df["trip_no"] = None

    df.loc[df_starts.index, "trip_no"] = trip_numbers
    df["trip_no"] = df["trip_no"].fillna(method="ffill")
    df["trip_no"] = df["trip_no"].fillna(start_number)

    return df


def get_starts(
    df: pd.DataFrame,
    trip_separator="0 days 00:01:00",
    separator_max_speed=1.0,
    initial_speed_separator=0.05,
) -> pd.DataFrame:
    """get start and end of complete trips from df.

    Parameters
    ----------
    df : pd.DataFrame
        Time series for all trips
    trip_separator : str, optional
        Time windows in the dataframe exceeding this time will divide the trips, by default '0 days 00:00:20'
    initial_speed_separator : float
        if the initial speed is lower than this, this is considered as a trip start also.

    Returns
    -------
    (pd.DataFrame, pd.DataFrame)
        df_starts,df_ends
        dataframes with rows from df with starts and ends.
    """

    df.sort_index(inplace=True)
    mask = df.index.to_series().diff() > trip_separator

    ## First part can be a begining of a trip:
    if df.iloc[0]["sog"] < initial_speed_separator:
        mask[0] = True

    df_starts = df.loc[mask]

    ## Also checking that the speed is low enough at the start:
    mask = df_starts["sog"] < separator_max_speed
    df_starts = df_starts.loc[mask]

    return df_starts.copy()


def add_trip_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add trip columns

    Adding columns:
    * "trip_time"
    * "trip_direction"
    * "reversing"

    Correcting columns:
    "heading"

    Parameters
    ----------
    df : pd.DataFrame
        data with "trip_no"

    Returns
    -------
    pd.DataFrame
        data with trip columns added/corrected
    """

    trips = df.groupby(by="trip_no")

    trip_time = trips["trip_no"].transform(lambda x: x.index - x.index[0])
    df["trip_time"] = pd.TimedeltaIndex(trip_time).total_seconds()

    # 0 : Helsingör -> Helsingborg
    # 1 : Helsingör <- Helsingborg
    df["trip_direction"] = trips["longitude"].transform(
        lambda x: "Helsingør-Helsingborg" if (x[0] < 12.65) else "Helsingborg-Helsingør"
    )

    ## Correcting apparent wind angle "Helsingborg-Helsingør"
    mask = df["trip_direction"] == "Helsingborg-Helsingør"
    df.loc[mask, "awa"] = np.mod(df.loc[mask, "awa"] + 180, 360)

    if ("cog" in df) and ("heading" in df):
        for trip_no, trip in trips:
            redefine_heading(df=df, trip=trip)

    if "heading" in df:
        df["drift_angle"] = df["heading"] - df["cog"]

    ## Derived quantities:
    awa = np.deg2rad(df["awa"])
    df["aw_x"] = df["aw"] * np.cos(awa)  # Apparent wind in ship x-direction
    df["aw_y"] = df["aw"] * np.sin(awa)  # Apparent wind in ship y-direction
    df["aw_x**2*sog"] = df["aw_x"] ** 2 * df["sog"]
    df["sog**3"] = df["sog"] ** 3

    if "drift_angle" in df:
        df["beta**2*sog"] = df["drift_angle"] ** 2 * df["sog"]

    return df


def redefine_heading(df: pd.DataFrame, trip):
    """The double ended ferry is run in reverse direction half of the time.
    This means that the "heading" measures by the compas is 180 degrees wrong, compared to course over ground from GPS.
    This method makes this 180 degrees heading shift whenever needed.

    Parameters
    ----------
    trip : pd.DataFrame
        [description]

    """

    heading = trip["heading"]
    cog = trip["cog"]
    awa = trip["awa"]

    if (cog - heading).abs().mean() > 90:
        df.loc[trip.index, "heading"] = np.mod(heading + 180, 360)
        # Also turning the apparent wind angle:
        df.loc[trip.index, "reversing"] = True
    else:
        df.loc[trip.index, "reversing"] = False
