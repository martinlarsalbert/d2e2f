import folium
import pandas as pd


def get_map(df: pd.DataFrame, width=1000, height=600, zoom_start=14):

    my_map = folium.Map(
        location=(df["latitude"].mean(), df["longitude"].mean()), zoom_start=zoom_start
    )
    f = folium.Figure(width=width, height=height)
    f.add_child(my_map)

    return f, my_map


def plot_map(
    df: pd.DataFrame,
    time_step="30S",
    width=1000,
    height=600,
    zoom_start=14,
    color_key="cog",
    colormap=["green", "red"],
):

    if time_step is None:
        df_ = df
    else:
        df_ = df.resample(time_step).mean()

    df_.dropna(subset=["latitude", "longitude"], inplace=True)

    my_map = folium.Map(
        location=(df_["latitude"].mean(), df_["longitude"].mean()),
        zoom_start=zoom_start,
    )

    points = df_[["latitude", "longitude"]].to_records(index=False)

    if df_[color_key].dtype == "object":
        mapping = {key: i for i, key in enumerate(df_[color_key].unique())}
        colors = list(df_[color_key].replace(mapping).values)
    else:
        colors = list(df_[color_key].values)

    line = folium.ColorLine(
        points, colors, colormap=colormap, opacity=0.30, popup="out", weight=1.0
    )
    line.add_to(my_map)

    f = folium.Figure(width=width, height=height)
    f.add_child(my_map)

    one_trip = False
    if "trip_no" in df:
        if len(df["trip_no"].unique()) == 1:
            one_trip = True

    if one_trip:

        start = df.iloc[0]
        stop = df.iloc[-1]

        folium.Marker(
            [start["latitude"], start["longitude"]],
            popup="start",
            icon=folium.Icon(color="green", icon="play"),
        ).add_to(my_map)
        folium.Marker(
            [stop["latitude"], stop["longitude"]],
            popup="stop",
            icon=folium.Icon(color="red", icon="stop"),
        ).add_to(my_map)

    return f


def plot_trips(
    df: pd.DataFrame,
    time_step="30S",
    width=1000,
    height=600,
    zoom_start=14,
    color_key="cog",
    colormap=["green", "red"],
):

    f, my_map = get_map(df=df, width=width, height=height, zoom_start=zoom_start)

    for trip_no, trip in df.groupby("trip_no"):

        df_ = trip.resample(time_step).mean()
        df_.dropna(subset=["latitude", "longitude"], inplace=True)

        points = df_[["latitude", "longitude"]].to_records(index=False)

        popup = "trip: %i" % trip_no
        color = "#00FF00" if trip.iloc[0]["trip_direction"] == 0 else "#FF0000"
        line = folium.PolyLine(
            points, opacity=0.30, popup=popup, weight=1.0, color=color
        )

        line.add_to(my_map)

    return f
