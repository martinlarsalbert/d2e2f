from kedro.pipeline import Pipeline, node

from .nodes import (
    join_files,
    slice,
    preprocess,
    preprocess_trip_numbering,
    preprocess_trip_columns,
)


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
                tags=["training", "inference"],
            ),
            node(
                func=slice,
                inputs=[
                    "raw_data_joined",
                    "params:row_start",
                    "params:row_end",
                ],
                outputs="raw_data_slice",
                name="slice_node",
                tags=["training", "inference"],
            ),
            node(
                func=preprocess,
                inputs=[
                    "raw_data_slice",
                    "params:renames",
                    "params:min_speed",
                ],
                outputs="preprocessed_data",
                name="preprocess_node",
                tags=["training", "inference"],
            ),
            node(
                func=preprocess_trip_numbering,
                inputs=[
                    "preprocessed_data",
                    "params:start_number",
                    "params:trip_separator",
                    "params:initial_speed_separator",
                ],
                outputs="data_with_trip_numbers",
                name="preprocess_trip_numbering_node",
                tags=["training", "inference"],
            ),
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
