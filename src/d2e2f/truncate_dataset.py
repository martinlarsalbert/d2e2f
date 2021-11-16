import pandas as pd
import os.path
import click


@click.command()
@click.argument("load_path")
@click.argument("save_dir_path")
@click.option("--chunksize", default=10 ** 5)
def truncate_dataset(load_path: str, save_dir_path, chunksize: int = 10 ** 5):
    do_truncate_dataset(
        load_path=load_path, save_dir_path=save_dir_path, chunksize=chunksize
    )


def do_truncate_dataset(load_path: str, save_dir_path, chunksize: int = 10 ** 5):
    file_name = os.path.split(load_path)[-1]
    save_path = os.path.join(save_dir_path, file_name)

    assert load_path != save_path, "Cannot load and save the same file"
    assert not os.path.exists(save_path), "Save file already exist"

    for chunk in pd.read_csv(load_path, chunksize=chunksize):
        assert isinstance(chunk, pd.DataFrame)
        chunk.to_csv(save_path)
        break


if __name__ == "__main__":
    truncate_dataset()
