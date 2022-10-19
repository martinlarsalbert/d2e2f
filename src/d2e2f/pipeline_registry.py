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

"""Project pipelines."""
from typing import Dict

from kedro.pipeline import Pipeline
from kedro.pipeline.modular_pipeline import pipeline
from pytest import param

from .pipelines import data_preprocessing as data_preprocessing
from .pipelines import trips_forsea as trips_forsea
from .pipelines import trips_uraniborg as trips_uraniborg
from .pipelines import trip_statistics as trip_statistics
from .pipelines import clean_thrusters_forsea as clean_thrusters_forsea
from .pipelines import train_test as train_test
from .pipelines import model_statistics as model_statistics
from .pipelines import load_datavarde
from .pipelines import load_vitskar

# from d2e2f.pipelines import join_files as js


def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipeline.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.

    """

    tycho = pipeline(
        data_preprocessing.create_pipeline()
        + trips_forsea.create_pipeline()
        + trip_statistics.create_pipeline()
        + clean_thrusters_forsea.create_pipeline()
        + train_test.create_pipeline()
        + model_statistics.create_pipeline(),
        namespace="tycho",
        parameters={"params:P_max": "params:tycho.P_max"},
    )

    aurora = pipeline(
        data_preprocessing.create_pipeline()
        + trips_forsea.create_pipeline()
        + trip_statistics.create_pipeline()
        + clean_thrusters_forsea.create_pipeline()
        + train_test.create_pipeline()
        + model_statistics.create_pipeline(),
        namespace="aurora",
        parameters={"params:P_max": "params:aurora.P_max"},
    )

    uraniborg = pipeline(
        data_preprocessing.create_pipeline()
        + trips_uraniborg.create_pipeline()
        + trip_statistics.create_pipeline(),
        namespace="uraniborg",
        # Changing the minimum distance and time for Uraniborg:ked
        parameters={
            "params:min_distance": "params:min_distance_uraniborg",
            "params:min_time": "params:min_time_uraniborg",
            "params:max_time": "params:max_time_uraniborg",
            "params:P_max": "params:uraniborg.P_max",
            "params:harbours": "params:uraniborg.harbours",
        },
    )

    load_vitaskar_pipeline = pipeline(
        load_vitskar.create_pipeline(),
        namespace="vitaskar",
        parameters={
            "params:load_start": "params:vitaskar.load_start",
            "params:load_end": "params:vitaskar.load_end",
        },
    )

    vitaskar = pipeline(
        data_preprocessing.create_pipeline()
        + trips_uraniborg.create_pipeline()
        + trip_statistics.create_pipeline(),
        namespace="vitaskar",
        # Changing the minimum distance and time for Uraniborg:ked
        parameters={
            "params:min_distance": "params:vitaskar.min_distance",
            "params:min_time": "params:vitaskar.min_time",
            "params:max_time": "params:vitaskar.max_time",
            "params:P_max": "params:vitaskar.P_max",
            "params:harbours": "params:vitaskar.harbours",
        },
    )

    the_pipeline = tycho + aurora + uraniborg + vitaskar

    namespace = "ssrs"
    load_datavarde_pipeline = pipeline(
        load_datavarde.create_pipeline(),
        namespace=namespace,
        parameters={
            "params:excludes": f"params:{namespace}.excludes",
            "params:exclude_ships": f"params:{namespace}.exclude_ships",
        },
    )

    return {
        "__default__": the_pipeline,
        "tycho": tycho,
        "aurora": aurora,
        "uraniborg": uraniborg,
        "vitaskar": vitaskar,
        "load_ssrs": load_datavarde_pipeline,
        "load_vitaskar": load_vitaskar_pipeline,
    }
