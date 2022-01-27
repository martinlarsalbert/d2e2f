import pandas as pd
import scipy.integrate
import numpy as np


def statistics(df: pd.DataFrame) -> pd.DataFrame:
    trips = df.groupby(by="trip_no")
    df_stat = trips.apply(func=trip_statistics)
    df_stat.index.name = "trip_no"
    return df_stat


def trip_statistics(trip: pd.DataFrame) -> pd.Series:

    assert isinstance(trip, pd.DataFrame)

    trip["time"] = trip.index

    assert (
        pd.TimedeltaIndex(trip["time"].diff().dropna()).total_seconds() > 0
    ).all()  # assert that rows are ordered in time

    start_time = trip.iloc[0]["time"]
    end_time = trip.iloc[-1]["time"]
    trip["trip_time"] = pd.TimedeltaIndex(trip["time"] - start_time).total_seconds()

    integrated = integrate_time(trip=trip)
    trip.drop(columns="time", inplace=True)
    df_statistics = trip.mean()

    df_statistics["start_time"] = str(start_time)
    df_statistics["end_time"] = str(end_time)

    ## Additional Integrated features:
    for i in range(1, 5):
        P_key = f"P{i}"
        if P_key in integrated:
            df_statistics[f"E{i}"] = integrated[P_key]

    if "P" in integrated:
        df_statistics["E"] = integrated["P"]

    df_statistics["distance"] = integrated["sog"]

    for i in range(1, 5, 1):
        key = f"Consumption ME{i} (L/h)"
        if key in integrated:
            df_statistics[f"Consumption ME{i} (L)"] = integrated[key] / 3600

    df_statistics["trip_time"] = (
        trip.iloc[-1]["trip_time"] - trip.iloc[0]["trip_time"]
    )  # Total trip time makes more sense.
    df_statistics["trip_no"] = int(trip.iloc[0]["trip_no"])

    if "reversing" in trip:
        df_statistics["reversing"] = trip.iloc[0]["reversing"]

    df_statistics["trip_direction"] = trip.iloc[0]["trip_direction"]

    return df_statistics


def integrate_time(trip):
    trip_ = trip.copy()
    t = trip_["trip_time"]
    assert t.dtype == "float64"

    X = trip_.select_dtypes(include=[np.float64])
    integral_trip = scipy.integrate.simps(y=X.T, x=t)

    s = pd.Series(data=integral_trip, name="integral", index=X.columns)

    return s
