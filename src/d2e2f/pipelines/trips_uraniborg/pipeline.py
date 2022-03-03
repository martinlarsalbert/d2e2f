"""
This is a boilerplate pipeline 'trips_uraniborg'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    preprocess_trip_columns,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=preprocess_trip_columns,
                inputs=[
                    "data_with_trip_numbers",
                ],
                outputs="data_with_trip_columns",
                name="preprocess_trip_columns_node",
                tags=["training", "inference"],
            ),
        ]
    )
