from kedro.pipeline import Pipeline, node

from .nodes import (
    join_files,
    slice,
    preprocess,
    numbering,
    find_trips,
    engine_load_to_power,
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
                    "params:P_max",
                ],
                outputs="data_prepared_",
                name="preprocess_node",
                tags=["training", "inference"],
            ),
            node(
                func=engine_load_to_power,
                inputs=[
                    "data_prepared_",
                    "engine_maximum_power_data",
                ],
                outputs="data_prepared",
                name="engine_load_to_power_node",
                tags=["training", "inference"],
            ),
            node(
                func=find_trips,
                inputs=[
                    "data_prepared",
                    "params:min_time",
                    "params:min_start_speed",
                ],
                outputs="data_start_end",
                name="find_trips",
                tags=["training", "inference"],
            ),
            node(
                func=numbering,
                inputs=[
                    "data_start_end",
                ],
                outputs="data_with_trip_numbers",
                name="numbering_node",
                tags=["training", "inference"],
            ),
        ]
    )
