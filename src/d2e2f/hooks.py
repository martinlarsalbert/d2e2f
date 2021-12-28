# Copyright 2021 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""Project hooks."""
from typing import Any, Dict, Iterable, Optional

from kedro.config import ConfigLoader
from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog
from kedro.versioning import Journal
from kedro.config import TemplatedConfigLoader


class ProjectHooks:
    @hook_impl
    def register_config_loader(self, conf_paths: Iterable[str]) -> ConfigLoader:
        return TemplatedConfigLoader(
            conf_paths,
            globals_pattern="*globals.yml",  # read the globals dictionary from project config
            globals_dict={  # extra keys to add to the globals dictionary, take precedence over globals_pattern
                "bucket_name": "another_bucket_name",
                "non_string_key": 10,
            },
        )

    @hook_impl
    def register_catalog(
        self,
        catalog: Optional[Dict[str, Dict[str, Any]]],
        credentials: Dict[str, Dict[str, Any]],
        load_versions: Dict[str, str],
        save_version: str,
        journal: Journal,
    ) -> DataCatalog:
        return DataCatalog.from_config(
            catalog, credentials, load_versions, save_version, journal
        )


from typing import Any, Dict

import mlflow
import mlflow.sklearn
from kedro.pipeline.node import Node

_active_run_stack = mlflow.tracking.fluent._active_run_stack


class ModelTrackingHooks:
    """Namespace for grouping all model-tracking hooks with MLflow together."""

    @hook_impl
    def after_catalog_created(self, catalog: DataCatalog) -> None:
        self.catalog = catalog

    @hook_impl
    def before_pipeline_run(self, run_params: Dict[str, Any]) -> None:
        """Hook implementation to start an MLflow run
        with the same run_id as the Kedro pipeline run.
        """
        mlflow.set_experiment("d2e2f")
        mlflow.start_run(run_name=run_params["run_id"])
        mlflow.log_params(run_params)

        for dataset_name, dataset in self.catalog.datasets.__dict__.items():
            if "raw_data" in dataset_name:
                mlflow.log_param(dataset_name, dataset._filepath)

    @hook_impl
    def before_node_run(self, node: Node, inputs: Dict[str, Any]) -> None:

        if not hasattr(self, "runs"):
            self.runs = {}

        if node._func_name == "slice":
            pass
            # mlflow.set_experiment("d2e2f")
            # self.runs[node.namespace] = mlflow.start_run(
            #    run_name=node.namespace, nested=True
            # )

    @hook_impl
    def after_node_run(
        self, node: Node, outputs: Dict[str, Any], inputs: Dict[str, Any]
    ) -> None:
        """Hook implementation to add model tracking after some node runs.
        In this example, we will:
        * Log the parameters after the data splitting node runs.
        * Log the model after the model training node runs.
        * Log the model's metrics after the model evaluating node runs.
        """

        # self.set_active_node(node=node)

        if node._func_name == "fit_linear_regression":

            model = outputs[
                f"{node.namespace}.trip_statistics_joined_thrusters_linear_regression_model"
            ]
            mlflow.sklearn.log_model(model, f"{node.namespace}_model")
            if "parameters" in inputs:
                mlflow.log_params(inputs[f"{node.namespace}_parameters"])

        elif node._func_name == "test":
            name_space_outputs = {
                f"{node.namespace}_{key}": value for key, value in outputs.items()
            }
            mlflow.log_metrics(name_space_outputs)

    @hook_impl
    def after_pipeline_run(self) -> None:
        """Hook implementation to end the MLflow run
        after the Kedro pipeline finishes.
        """
        mlflow.end_run()

    def set_active_node(self, node):
        """(Not used)

        Parameters
        ----------
        node : [type]
            [description]
        """
        run = self.runs[node.namespace]
        for i, run_ in enumerate(_active_run_stack):
            if run.info.run_id == run_.info.run_id:
                break
        item = _active_run_stack.pop(i)
        _active_run_stack.insert(0, item)
