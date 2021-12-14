import pandas as pd
from kedro.io import PartitionedDataSet
import numpy as np
from typing import Union
from .linear_regression import fit, features, label
from sklearn.metrics import mean_squared_error
import logging


# def fit_linear_regression(loaded: PartitionedDataSet) -> PartitionedDataSet:
#    partitions = {}
#    for partition_id, partition_load_func in loaded.items():
#        df = partition_load_func()
#        new_file_name = partition_id.replace(".parquet", ".pickle")
#        partitions[new_file_name] = _fit_linear_regression(df=df)
#
#    return partitions


def fit_linear_regression(df: pd.DataFrame) -> pd.DataFrame:

    return fit(df=df)


# def test(
#    test_data: PartitionedDataSet, models: PartitionedDataSet
# ) -> PartitionedDataSet:
#    partitions = {}
#    for partition_id, partition_load_func in test_data.items():
#        df = partition_load_func()
#        model_id = partition_id.replace(".parquet", ".pickle")
#        model = models[model_id]()
#        _test(df=df, model=model, model_id=model_id)


def test(df: pd.DataFrame, model):

    X = features(df=df)
    y = label(df=df)
    y_pred = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y_true=y, y_pred=y_pred))

    # log = logging.getLogger(__name__)
    # log.info(f"Model accuracy with {model_id} on test set rmse: {rmse}")
    return rmse


# def inference(
#    data: PartitionedDataSet, models: PartitionedDataSet
# ) -> PartitionedDataSet:
#    partitions = {}
#    for partition_id, partition_load_func in data.items():
#        df = partition_load_func()
#        model_id = partition_id.replace(".parquet", ".pickle")
#        model = models[model_id]()
#        partitions[partition_id] = _inference(df=df, model=model, model_id=model_id)
#
#    return partitions


def inference(df: pd.DataFrame, model):

    X = features(df=df)

    y_pred = model.predict(X)

    df_pred = df.copy()
    df_pred["P"] = y_pred

    return df_pred
