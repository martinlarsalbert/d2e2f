import json

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

import dash_leaflet as dl

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "D2E2F Dashboard"

styles = {"pre": {"border": "thin lightgrey solid", "overflowX": "scroll"}}


df_statistics = pd.read_parquet(
    "../../data/02_intermediate/uraniborg_trip_statistics_clean.parquet"
    # "../../data/02_intermediate/aurora_trip_statistics_clean.parquet"
)

df = pd.read_parquet(
    "../../data/02_intermediate/uraniborg_data_with_trip_columns.parquet"
    # "../../data/02_intermediate/aurora_data_with_trip_columns.parquet"
)
df["trip_no"] = df["trip_no"].astype(int)
trips = df.groupby(by="trip_no")
trips_selected = trips.get_group(list(trips.groups.keys())[0])

fig_statistics = px.scatter(
    df_statistics,
    x="start_time",
    y="E",
    color="trip_direction",
    custom_data=["trip_no"],
    height=300,
)
fig_statistics.update_layout(clickmode="event+select")
fig_statistics.update_traces(marker_size=10)


def plot_trips(trips_selected, key="P"):

    fig = px.line(
        trips_selected,
        x="trip_time",
        y=key,
        color="trip_no",
        height=300,
    )

    fig_trips_yaxis_range = [0, df[key].max()]
    fig_trips_xaxis_range = [df["trip_time"].min(), df["trip_time"].max()]
    fig.update_yaxes(range=fig_trips_yaxis_range)
    fig.update_xaxes(range=fig_trips_xaxis_range)

    return fig


fig_trips_P = plot_trips(trips_selected=trips_selected, key="P")
fig_trips_sog = plot_trips(trips_selected=trips_selected, key="sog")
fig_trips_w = plot_trips(trips_selected=trips_selected, key="w")

map = dl.Map(
    [dl.TileLayer(), dl.LayerGroup(id="trips")],
    style={"width": f"1500px", "height": f"300px"},
    center=[df["latitude"].mean(), df["longitude"].mean()],
    zoom=14,
    id="map",
)


app.layout = html.Div(
    [
        dcc.Graph(
            id="basic-interactions",
            figure=fig_statistics,
        ),
        map,
        dcc.Graph(
            id="figure_trips_P",
            figure=fig_trips_P,
        ),
        dcc.Graph(
            id="figure_trips_sog",
            figure=fig_trips_sog,
        ),
        dcc.Graph(
            id="figure_trips_w",
            figure=fig_trips_w,
        ),
    ]
)


@app.callback(
    [
        Output("figure_trips_P", "figure"),
        Output("figure_trips_sog", "figure"),
        Output("figure_trips_w", "figure"),
    ],
    Input("basic-interactions", "selectedData"),
)
def update_trips(clickData):

    if clickData is None:
        trip_nos = [list(trips.groups.keys())[0]]
    else:
        points = clickData["points"]
        trip_nos = [point["customdata"][0] for point in points]

    trips_selected = [trips.get_group(trip_no) for trip_no in trip_nos]
    trips_selected = pd.concat(trips_selected)

    fig_trips = px.line(
        trips_selected,
        x="trip_time",
        y="P",
        color="trip_no",
        height=300,
    )
    fig_trips_P = plot_trips(trips_selected=trips_selected, key="P")
    fig_trips_sog = plot_trips(trips_selected=trips_selected, key="sog")
    fig_trips_w = plot_trips(trips_selected=trips_selected, key="w")

    return fig_trips_P, fig_trips_sog, fig_trips_w


@app.callback(
    Output("trips", "children"), [Input("basic-interactions", "selectedData")]
)
def update_map(clickData, time_step="30S"):

    if clickData is None:
        trip_nos = [list(trips.groups.keys())[0]]
    else:
        points = clickData["points"]
        trip_nos = [point["customdata"][0] for point in points]

    trips_selected = [trips.get_group(trip_no) for trip_no in trip_nos]
    trips_selected = pd.concat(trips_selected)

    lines = []
    for trip_no, trip in trips_selected.groupby("trip_no"):
        df_ = trip.resample(time_step).mean()
        df_.dropna(subset=["latitude", "longitude"], inplace=True)
        points = df_[["latitude", "longitude"]].to_records(index=False)
        line = dl.Polyline(
            positions=points,
            opacity=0.30,
        )
        lines.append(line)

    return lines


if __name__ == "__main__":
    app.run_server(debug=True)
