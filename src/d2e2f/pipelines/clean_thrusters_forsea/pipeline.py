"""
This is a boilerplate pipeline 'clean_thrusters_forsea'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    clean_thrusters,
    outliers_thrusters,
    join_thrusters,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=clean_thrusters,
                inputs=[
                    "trip_statistics_clean",
                    "params:P_max_ratio_diff",
                    "params:cos_ratio_diff",
                ],
                outputs="trip_statistics_clean_thrusters",
                name="clean_thrusters_node",
                tags=["training", "inference"],
            ),
            node(
                func=outliers_thrusters,
                inputs=[
                    "trip_statistics_clean",
                    "params:P_max_ratio_diff",
                    "params:cos_ratio_diff",
                ],
                outputs="trip_statistics_clean_thrusters_outliers",
                name="outliers_thrusters_node",
                tags=["training"],
            ),
            node(
                func=join_thrusters,
                inputs=[
                    "trip_statistics_clean_thrusters",
                ],
                outputs="trip_statistics_joined_thrusters",
                name="join_thrusters_node",
                tags=["training", "inference"],
            ),
        ]
    )
