import pandas as pd
import pytest

import os.path
import yaml

test_data_path = os.path.join(
    os.path.split(os.path.split(os.path.dirname(__file__))[0])[0], "test_data"
)


@pytest.fixture(scope="module")
def parameters():
    filepath = os.path.join(
        test_data_path,
        "parameters.yml",
    )

    with open(filepath) as file:
        pars = yaml.safe_load(file)

    return pars


@pytest.fixture(scope="module")
def catalog():
    from kedro.io import DataCatalog
    from kedro.extras.datasets.pandas import (
        CSVDataSet,
        # ParquetDataSet,
    )

    datasets = {
        "raw_data": CSVDataSet(
            filepath=os.path.join(
                test_data_path,
                "tycho-brahe-wind-2021-04-10--2021-06-30.csv",
            )
        ),
    }
    # parameters = {f"params:{key}": value for key, value in parameters.items()}
    # datasets.update(parameters)

    io = DataCatalog(datasets)

    return io
