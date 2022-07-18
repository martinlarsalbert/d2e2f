"""
This is a boilerplate pipeline 'load_datavarde'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node
from .nodes import (
    load,
    join_telematikenheter,
    clean,
    select_columns,
    speed_select,
    statistics,
    statistics_summary,
)


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                load,
                inputs=["raw_data", "params:excludes"],
                outputs=["telematikenheter", "units", "data_descriptions"],
                tags=["telematikenheter"],
            ),
            node(
                join_telematikenheter,
                inputs=["telematikenheter", "params:resample_period"],
                outputs="data",
                tags=["join"],
            ),
            node(
                clean,
                inputs=["data"],
                outputs="clean_data",
                tags=["clean"],
                name="clean",
            ),
            node(
                select_columns,
                inputs=["clean_data", "data_descriptions"],
                outputs="data_selected",
                tags=["select"],
                name="select",
            ),
            node(
                speed_select,
                inputs=["data_selected", "params:moving_min_speed"],
                outputs="data_moving",
                tags=["speed_select"],
            ),
            node(
                speed_select,
                inputs=["data_selected", "params:running_min_speed"],
                outputs="data_running",
                tags=["speed_select"],
            ),
            ## Statistics
            node(
                statistics,
                inputs=["data_selected", "params:resample_period"],
                outputs="statistics",
                tags=["statistics"],
            ),
            node(
                statistics,
                inputs=["data_moving", "params:resample_period"],
                outputs="statistics_moving",
                tags=["statistics"],
            ),
            node(
                statistics,
                inputs=["data_running", "params:resample_period"],
                outputs="statistics_running",
                tags=["statistics"],
            ),
            node(
                statistics_summary,
                inputs=["statistics"],
                outputs="statistics_summary",
                tags=["summary", "statistics"],
            ),
            node(
                statistics_summary,
                inputs=["statistics_moving"],
                outputs="statistics_moving_summary",
                tags=["summary", "statistics"],
            ),
            node(
                statistics_summary,
                inputs=["statistics_running"],
                outputs="statistics_running_summary",
                tags=["summary", "statistics"],
            ),
        ]
    )
