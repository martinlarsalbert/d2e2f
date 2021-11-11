from kedro.pipeline import Pipeline, node

from .nodes import preprocess_trip_statistics, preprocess_clean_statistics


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
            node(
                func=preprocess_clean_statistics,
                inputs=[
                    "trip_statistics",
                    "params:min_distance",
                    "params:min_time",
                ],
                outputs="trip_statistics_clean",
                name="preprocess_clean_statistics_node",
            ),
        ]
    )
