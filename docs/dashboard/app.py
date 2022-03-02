import json

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = Dash(__name__, external_stylesheets=external_stylesheets)

styles = {"pre": {"border": "thin lightgrey solid", "overflowX": "scroll"}}

# df = pd.DataFrame(
#    {
#        "x": [1, 2, 1, 2],
#        "y": [1, 2, 3, 4],
#        "customdata": [1, 2, 3, 4],
#        "fruit": ["apple", "apple", "orange", "orange"],
#    }
# )

df_statistics = pd.read_parquet(
    # "../../data/02_intermediate/uraniborg_trip_statistics_clean.parquet"
    "../../data/02_intermediate/aurora_trip_statistics_clean.parquet"
)

df = pd.read_parquet(
    # "../../data/02_intermediate/uraniborg_trip_statistics_clean.parquet"
    "../../data/02_intermediate/aurora_data_with_trip_columns.parquet"
)
df["trip_no"] = df["trip_no"].astype(int)
trips = df.groupby(by="trip_no")
trips_selected = trips.get_group(list(trips.groups.keys())[0])

fig_statistics = px.scatter(
    df_statistics,
    x="sog",
    y="E",
    color="trip_direction",
    custom_data=["trip_no"],
)

fig_trips = px.line(
    trips_selected,
    x="trip_time",
    y="P",
    color="trip_no",
)

fig_statistics.update_layout(clickmode="event+select")
fig_statistics.update_traces(marker_size=10)

app.layout = html.Div(
    [
        dcc.Graph(id="basic-interactions", figure=fig_statistics),
        dcc.Graph(id="figure_trips", figure=fig_trips),
        html.Div(
            className="row",
            children=[
                html.Div(
                    [
                        dcc.Markdown(
                            """
                **Hover Data**

                Mouse over values in the graph.
            """
                        ),
                        html.Pre(id="hover-data", style=styles["pre"]),
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        dcc.Markdown(
                            """
                **Click Data**

                Click on points in the graph.
            """
                        ),
                        html.Pre(id="click-data", style=styles["pre"]),
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        dcc.Markdown(
                            """
                **Selection Data**

                Choose the lasso or rectangle tool in the graph's menu
                bar and then select points in the graph.

                Note that if `layout.clickmode = 'event+select'`, selection data also
                accumulates (or un-accumulates) selected data if you hold down the shift
                button while clicking.
            """
                        ),
                        html.Pre(id="selected-data", style=styles["pre"]),
                    ],
                    className="three columns",
                ),
                html.Div(
                    [
                        dcc.Markdown(
                            """
                **Zoom and Relayout Data**

                Click and drag on the graph to zoom or click on the zoom
                buttons in the graph's menu bar.
                Clicking on legend items will also fire
                this event.
            """
                        ),
                        html.Pre(id="relayout-data", style=styles["pre"]),
                    ],
                    className="three columns",
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("hover-data", "children"), Input("basic-interactions", "hoverData")
)
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output("click-data", "children"), Input("basic-interactions", "clickData")
)
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output("figure_trips", "figure"), Input("basic-interactions", "selectedData")
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
    )

    return fig_trips


@app.callback(
    Output("selected-data", "children"), Input("basic-interactions", "selectedData")
)
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)


@app.callback(
    Output("relayout-data", "children"), Input("basic-interactions", "relayoutData")
)
def display_relayout_data(relayoutData):
    return json.dumps(relayoutData, indent=2)


if __name__ == "__main__":
    app.run_server(debug=True)
