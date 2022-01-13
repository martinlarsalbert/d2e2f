"""
This is a boilerplate pipeline 'train_test'
generated using Kedro 0.17.6
"""

import pandas as pd
from kedro.io import PartitionedDataSet
import numpy as np
from typing import Union


def train_test_split(
    df: pd.DataFrame, test_ratio=0.2
) -> Union[pd.DataFrame, pd.DataFrame]:
    """Split the dataframe into one for training and another one for testing
    Note! The test dataset is taken from the "future" happening after the train dataset

    Parameters
    ----------
    loaded : PartitionedDataSet
        [description]
    test_ratio : float, optional
        how much of the data is used for testing?, by default 0.2

    Returns
    -------
    Union[PartitionedDataSet, PartitionedDataSet]
        partitions_train, partitions_test
    """

    train_index = int(np.floor((1 - test_ratio) * len(df)))
    df_train = df.iloc[0:train_index]
    df_test = df.iloc[train_index:]

    return df_train, df_test
