"""
This is a boilerplate pipeline 'load_datavarde'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node
from .nodes import load


def create_pipeline(**kwargs):
    return Pipeline(
        [node(load, inputs=["raw_data", "params:excludes"], outputs="data")]
    )
