import pandas as pd
import scipy.integrate
import numpy as np


def statistics(df: pd.DataFrame) -> pd.DataFrame:
    trips = df.groupby(by="trip_no")
    return trips.apply(func=trip_statistics)


def trip_statistics(trip: pd.DataFrame) -> pd.Series:

    assert isinstance(trip, pd.DataFrame)

    trip["time"] = pd.to_datetime(trip["time"])

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
    df_statistics["E1"] = integrated["P1"]
    df_statistics["E2"] = integrated["P2"]
    df_statistics["E3"] = integrated["P3"]
    df_statistics["E4"] = integrated["P4"]
    df_statistics["E"] = integrated["P"]
    #
    df_statistics["distance"] = integrated["sog"]

    df_statistics["trip_time"] = (
        trip.iloc[-1]["trip_time"] - trip.iloc[0]["trip_time"]
    )  # Total trip time makes more sense.
    df_statistics["trip_no"] = trip.iloc[0]["trip_no"]
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
