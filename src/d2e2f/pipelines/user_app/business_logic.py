from d2e2f.pipelines.model_statistics.nodes import _inference
from kedro.io import PartitionedDataSet


def predict_with_mlflow(
    data: PartitionedDataSet, models: PartitionedDataSet
) -> PartitionedDataSet:

    partitions = {}
    for partition_id, partition_load_func in data.items():
        df = partition_load_func()
        model_id = partition_id.replace(".parquet", ".pickle")
        model = models[model_id]()
        partitions[partition_id] = _inference(df=df, model=model, model_id=model_id)

    return partitions
