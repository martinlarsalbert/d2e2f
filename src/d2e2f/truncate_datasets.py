import click
import os
from truncate_dataset import do_truncate_dataset
import logging


@click.command()
@click.argument("load_dir_path")
@click.argument("save_dir_path")
@click.option("--chunksize", default=10 ** 5)
def truncate_datasets(load_dir_path: str, save_dir_path, chunksize: int = 10 ** 5):

    if not os.path.exists(save_dir_path):
        os.makedirs(save_dir_path)

    for file in os.listdir(load_dir_path):

        load_path = os.path.join(load_dir_path, file)
        do_truncate_dataset(
            load_path=load_path, save_dir_path=save_dir_path, chunksize=chunksize
        )
        logging.info(f"{file}")


if __name__ == "__main__":
    truncate_datasets()
