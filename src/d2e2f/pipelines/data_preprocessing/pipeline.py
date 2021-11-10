from kedro.pipeline import Pipeline, node

from .nodes import preprocess, preprocess_trip_numbering


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=preprocess,
                inputs=[
                    "raw_data",
                    "params:renames",
                ],
                outputs="preprocessed_data",
                name="preprocess_node",
            ),
            node(
                func=preprocess_trip_numbering,
                inputs=[
                    "preprocessed_data",
                    "params:start_number",
                ],
                outputs="data_with_trip_numbers",
                name="preprocess_trip_numbering_node",
            ),
        ]
    )
