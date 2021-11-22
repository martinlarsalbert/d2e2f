from kedro.pipeline import Pipeline, node

from d2e2f.pipelines.user_app.business_logic import predict_with_mlflow


def create_pipeline(**kwargs):
    pipeline_user_app = Pipeline(
        [
            node(
                func=predict_with_mlflow,
                inputs=dict(
                    data="raw_data",
                    model="trip_statistics_joined_thrusters_linear_regression_model",
                ),
                outputs="predictions",
                tags="user_app",
            )
        ]
    )

    return pipeline_user_app
