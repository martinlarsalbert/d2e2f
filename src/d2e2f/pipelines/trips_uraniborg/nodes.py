"""
This is a boilerplate pipeline 'trips_uraniborg'
generated using Kedro 0.17.6
"""
"""
This is a boilerplate pipeline 'trips_forsea'
generated using Kedro 0.17.6
"""

import pandas as pd
import numpy as np
from d2e2f import apparent_wind
from d2e2f.pipelines.trip_statistics.trip_statistics import mean_angle_deg


def preprocess_trip_columns(
    df: pd.DataFrame, harbours: list = ["harbour 1", " harbour 2"]
) -> pd.DataFrame:
    df = add_trip_columns(df=df, harbours=harbours)
    return df


def add_trip_columns(df: pd.DataFrame, harbours: list) -> pd.DataFrame:
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

    # Remove points between trips:
    mask = df["trip_no"] != -1  # Remove time between trips
    df = df.loc[mask].copy()

    trips = df.groupby(by="trip_no")

    trip_time = trips["trip_no"].transform(lambda x: x.index - x.index[0])
    df["trip_time"] = pd.TimedeltaIndex(trip_time).total_seconds()

    # df["trip_direction"] = trips["longitude"].transform(
    #    lambda x: "Ven-Landskrona" if (x[0] < x.quantile(0.10)) else "Landskrona-Ven"
    # )

    dx_limit = np.cos(np.deg2rad(df["cog"]).quantile(0.5))
    dy_limit = np.sin(np.deg2rad(df["cog"]).quantile(0.5))
    cog_limit = np.mod(np.rad2deg(np.arctan2(dy_limit, dx_limit)), 360)
    harbour1 = list(harbours.keys())[0]
    harbour2 = list(harbours.keys())[1]
    df["trip_direction"] = trips["cog"].transform(
        lambda x: f"{harbour1}-{harbour2}"
        if (mean_angle_deg(x) < cog_limit)
        else f"{harbour2}-{harbour1}"
    )

    df["thrust_factor"] = np.where(
        df["trip_direction"] == "Landskrona-Ven",
        df["Consumption ME1 (L/h)"] / df["consumption"],
        df["Consumption ME2 (L/h)"] / df["consumption"],
    )

    ## Correcting apparent wind angle "Helsingborg-Helsingør"
    # mask = df["trip_direction"] == "Helsingborg-Helsingør"
    # df.loc[mask, "awa"] = np.mod(df.loc[mask, "awa"] + 180, 360)

    if ("cog" in df) and ("heading" in df):
        for trip_no, trip in trips:
            redefine_heading(df=df, trip=trip)

    if "heading" in df:
        df["drift_angle"] = df["heading"] - df["cog"]

    if "awa" in df:
        # (This is the only thing that makes sense)
        df["awa"] += 180

        # True wind:
        aw = df["aw"]
        awa = np.deg2rad(df["awa"])
        sog = df["sog"]
        df["w"] = apparent_wind.apparent_wind_to_true(sog=sog, aw=aw, awa=awa)
        df["wa"] = np.mod(
            np.rad2deg(
                apparent_wind.apparent_wind_angle_to_true(sog=sog, aw=aw, awa=awa)
            ),
            360,
        )

        ## Derived quantities:
        awa = np.deg2rad(df["awa"])
        df["aw_x"] = df["aw"] * np.cos(awa)  # Apparent wind in ship x-direction
        df["aw_y"] = df["aw"] * np.sin(awa)  # Apparent wind in ship y-direction
        df["aw_x**2*sog"] = df["aw_x"].abs() * df["aw_x"] * df["sog"]

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
