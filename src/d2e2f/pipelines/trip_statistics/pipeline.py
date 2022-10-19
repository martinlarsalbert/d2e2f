from kedro.pipeline import Pipeline, node

from .nodes import (
    preprocess_trip_statistics,
    preprocess_clean_statistics,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=preprocess_trip_statistics,
                inputs=[
                    "data_with_trip_columns",
                    "params:max_time_diff",
                ],
                outputs="trip_statistics",
                name="preprocess_trip_statistics_node",
                tags=["training", "inference"],
            ),
            node(
                func=preprocess_clean_statistics,
                inputs=[
                    "trip_statistics",
                    "params:min_distance",
                    "params:min_time",
                    "params:max_time",
                ],
                outputs="trip_statistics_clean",
                name="preprocess_clean_statistics_node",
                tags=["training", "inference"],
            ),
        ]
    )
