import pandas as pd
from kedro.io import PartitionedDataSet


def join_files(loaded: PartitionedDataSet) -> pd.DataFrame:
    """[summary]

    Parameters
    ----------
    loaded : PartitionedDataSet
        Dataset from many files

    Returns
    -------
    pd.DataFrame
        join the files in onw dataframe to be used in the rest of the pipeline
        column "source" is added with the file name of the data
    """

    partitions = {}
    for partition_id, partition_load_func in loaded.items():
        df = partition_load_func()
        df["source"] = partition_id

        # combine_all = pd.concat([combine_all, df], axis=0, ignore_index=True)
        partitions[partition_id] = df

    return partitions
