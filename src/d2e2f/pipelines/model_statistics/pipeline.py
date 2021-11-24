from kedro.pipeline import Pipeline, node

from .nodes import fit_linear_regression, test, inference


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
                tags=["training", "inference"],
            ),
            node(
                func=test,
                inputs=[
                    "trip_statistics_joined_thrusters_test",
                    "trip_statistics_joined_thrusters_linear_regression_model",
                ],
                outputs="rmse",
                name="test_linear_regression_node",
                tags=["training"],
            ),
            node(
                func=inference,
                inputs=[
                    "trip_statistics_joined_thrusters",
                    "trip_statistics_joined_thrusters_linear_regression_model",
                ],
                outputs="trip_statistics_joined_thrusters_linear_regression_prediction",
                name="inference_linear_regression_node",
                tags=["inference"],
            ),
        ]
    )
