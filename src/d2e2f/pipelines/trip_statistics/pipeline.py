from kedro.pipeline import Pipeline, node

from .nodes import (
    preprocess_trip_statistics,
    preprocess_clean_statistics,
    clean_thrusters,
    join_thrusters,
    train_test_split,
)


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
            node(
                func=clean_thrusters,
                inputs=[
                    "trip_statistics_clean",
                    "params:P_max_ratio_diff",
                    "params:cos_ratio_diff",
                ],
                outputs=[
                    "trip_statistics_clean_thrusters",
                    "trip_statistics_clean_thrusters_outliers",
                ],
                name="clean_thrusters_node",
            ),
            node(
                func=join_thrusters,
                inputs=[
                    "trip_statistics_clean_thrusters",
                ],
                outputs="trip_statistics_joined_thrusters",
                name="join_thrusters_node",
            ),
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
            ),
        ]
    )
