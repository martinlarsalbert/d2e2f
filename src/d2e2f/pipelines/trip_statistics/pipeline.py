from kedro.pipeline import Pipeline, node

from .nodes import preprocess_trip_statistics


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=preprocess_trip_statistics,
                inputs=[
                    "data_with_trip_columns",
                ],
                outputs="trip_statistics",
                name="preprocess_trip_statistics_node",
            ),
        ]
    )
