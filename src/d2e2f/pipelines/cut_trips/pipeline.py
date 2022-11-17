"""
This is a boilerplate pipeline 'cut_trips'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node
from .nodes import steaming

# from src.master_thesis.pipelines.trip_statistics import preprocess_trip_statistics


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=steaming,
                inputs=[
                    "data_with_trip_columns",
                    "params:min_steaming_longitude",
                    "params:max_steaming_longitude",
                ],
                outputs="data_steaming",
            ),
        ]
    )
