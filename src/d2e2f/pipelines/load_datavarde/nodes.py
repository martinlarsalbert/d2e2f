"""
This is a boilerplate pipeline 'load_datavarde'
generated using Kedro 0.17.6
"""

import pandas as pd
from pathlib import Path
import numpy as np
import logging

log = logging.getLogger(__name__)


def load(data: dict, excludes=[], limit=np.inf) -> pd.DataFrame:

    # Divide all data per ship:
    ship_parts = {}
    count = 0
    for key, loader in data.items():

        path = Path(key)
        ship = path.parts[0]
        directory = path.parts[1]

        # exclude signals:
        if np.any(
            np.array([exclude.lower() in directory.lower() for exclude in excludes])
        ):
            continue

        if "SSRS" in directory:
            continue  # skipping these strange folders...

        part = loader()
        if not ship in ship_parts:
            ship_parts[ship] = []

        ship_parts[ship].append(part)

        count += 1
        if count > limit:
            break

    log.info(f"found data for ships:{ship_parts.keys()}")

    dataframes = {}
    for ship, parts in ship_parts.items():
        log.info(f"loading ship:{ship}")

        data = load_ship(parts=parts)
        dataframes[ship] = data_to_frame(data=data)

    return dataframes


def load_ship(parts: list, limit=np.inf):

    data = {}
    counter = 0
    for part in parts:
        for index, row in part.iterrows():

            name = str(row["signal"])
            content = row["decimated_signal"]
            if "LAT-LON" in name:

                name = "latitude"
                values = [item["value"][0] for item in content.values()]
                save_signal(row=row, name=name, data=data, values=values)

                name = "longitude"
                values = [item["value"][1] for item in content.values()]
                save_signal(row=row, name=name, data=data, values=values)

            else:
                values = [item["value"] for item in content.values()]

                save_signal(row=row, name=name, data=data, values=values)

            counter += 1

            if counter > limit:
                break

        if counter > limit:
            break

    # Resampling an removing duplicates (why are there duplicates???)
    data2 = {
        key: s[~s.index.duplicated()].resample("10S").interpolate()
        for key, s in data.items()
    }

    return data2


def data_to_frame(data: dict) -> pd.DataFrame:

    df = pd.DataFrame()
    for key, values in data.items():

        if len(df) == 0:
            df = values.to_frame()
        else:
            df = df.combine_first(values.to_frame())

    return df


def save_signal(row, name: str, data, values):

    content = row["decimated_signal"]
    index = content.keys()

    s = pd.Series(data=values, index=index, name=name, dtype=float)

    s.index = s.index.astype(int)
    s.index = pd.to_datetime(s.index, unit="s")
    s.sort_index(inplace=True)

    if not name in data:
        data[name] = s
    else:
        data[name] = data[name].append(s)
