from kedro.pipeline import Pipeline, node

from .nodes import join_files


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=join_files,
                inputs=[
                    "raw_data",
                ],
                outputs="raw_data_joined",
                name="join_files_node",
            ),
        ]
    )
