from kedro.pipeline import Pipeline, node

from .nodes import fit_linear_regression, test


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=fit_linear_regression,
                inputs=[
                    "trip_statistics_joined_thrusters_train",
                ],
                outputs="trip_statistics_joined_thrusters_linear_regression_model",
                name="fit_linear_regression_node",
            ),
            node(
                func=test,
                inputs=[
                    "trip_statistics_joined_thrusters_train",
                    "trip_statistics_joined_thrusters_linear_regression_model",
                ],
                outputs=None,
                name="test_linear_regression_node",
            ),
        ]
    )
