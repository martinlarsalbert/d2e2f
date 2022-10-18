"""
This is a boilerplate pipeline 'load_vitskar'
generated using Kedro 0.17.6
"""

from kedro.pipeline import Pipeline, node
from .nodes import load_blueflow


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                load_blueflow,
                inputs=["params:load_start", "params:load_end"],
                outputs="raw_data",
            )
        ]
    )
