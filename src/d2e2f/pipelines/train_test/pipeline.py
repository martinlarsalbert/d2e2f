"""
This is a boilerplate pipeline 'train_test'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    train_test_split,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=train_test_split,
                inputs=[
                    "trip_statistics_joined_thrusters",
                ],
                outputs=[
                    "trip_statistics_joined_thrusters_train",
                    "trip_statistics_joined_thrusters_test",
                ],
                name="train_test_split_node",
                tags=["training"],
            ),
        ]
    )
