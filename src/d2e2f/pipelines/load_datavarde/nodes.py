"""
This is a boilerplate pipeline 'load_datavarde'
generated using Kedro 0.17.6
"""

from asyncio.log import logger
import pandas as pd
from pathlib import Path
import numpy as np
import logging
import scipy.integrate
import sklearn

log = logging.getLogger(__name__)

import geopandas

from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures, SplineTransformer


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

    # dataframes = {}
    units = {}
    datas = {}
    data_descriptions = {}
    for ship, parts in ship_parts.items():

        log.info(f"loading ship:{ship}")

        data, units[ship] = load_ship(parts=parts)
        data_global_keys = {fr"{ship}/{key}": values for key, values in data.items()}
        datas.update(data_global_keys)

        descriptions_global_keys = {
            fr"{ship}/{key}": {k: float(v) for k, v in values.describe().items()}
            for key, values in data.items()
        }
        data_descriptions.update(descriptions_global_keys)

        # dataframes[ship] = data_to_frame(data=data)

    return datas, units, data_descriptions


def load_ship(parts: list, limit=np.inf):

    data = {}
    counter = 0
    units = {}

    for part in parts:
        for index, row in part.iterrows():

            name = str(row["signal"])
            content = row["decimated_signal"]
            if "unit" in row:
                units[name] = row["unit"]

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
    # data2 = {
    #    key: s[~s.index.duplicated()].resample("10S").interpolate()
    #    for key, s in data.items()
    # }

    return data, units


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


def join_telematikenheter(telematikenheter: dict, resample_period: float) -> dict:

    dataframes = {}

    # Restructure the loader per ship:
    ship_loaders = {}
    for key, loader in telematikenheter.items():
        ship = Path(key).parts[0]
        telematikenhet = Path(key).parts[1]

        if not ship in ship_loaders:
            ship_loaders[ship] = {}

        ship_loaders[ship][telematikenhet] = loader

    for ship, loaders in ship_loaders.items():
        logger.info(f"ship: {ship}")
        data = {key: loader() for key, loader in loaders.items()}
        dataframes[ship] = data_to_frame(data, resample_period=resample_period)

    return dataframes


def data_to_frame(data: dict, resample_period) -> pd.DataFrame:

    df = pd.DataFrame()
    for key, values in data.items():
        logger.info(key)
        values.index = pd.to_datetime(values.index)
        # resample_values = (
        #    values[~values.index.duplicated()]
        #    .sort_index()
        #    .resample(f"{resample_period}S")
        #    .interpolate()  # Resampling an removing duplicates (why are there duplicates???)
        # )
        resample_values = _resample(
            df=values[
                ~values.index.duplicated()
            ].sort_index(),  # Resampling an removing duplicates (why are there duplicates???)
            resample_period=resample_period,
        )

        if len(df) == 0:
            df = resample_values
        else:
            df = df.combine_first(resample_values)

    df.index.name = "time"

    return df


def _resample(df: pd.DataFrame, resample_period, max_time_gap="600S") -> pd.DataFrame:
    """Group data when max_time_gap is exceeded and then resample.
    This avoids that large time gaps are filled with interpolation.

    Parameters
    ----------
    s : pd.Series
        _description_
    resample_period : _type_
        _description_
    max_time_gap : str, optional
        _description_, by default "10S"

    Returns
    -------
    pd.Series
        _description_
    """
    mask = np.concatenate(([True], (df.index[1:] - df.index[0:-1]) > max_time_gap))
    n_groups = mask.sum()
    df.loc[mask, "group"] = np.arange(0, n_groups)
    df["group"] = df["group"].ffill()
    groups = []
    for group, df_group in df.groupby(by=["group"], sort=False):
        groups.append(
            df_group.resample(f"{resample_period}S")
            .interpolate()
            .drop(columns=["group"])
        )

    df_resample = pd.concat(groups)

    return df_resample


def _quantile_clean(data: pd.DataFrame, columns: list = None, alpha=0.001):

    if columns is None:
        columns = data.columns

    for key in columns:
        values = data[key]
        mask = (values.quantile(alpha) < values) & (values.quantile(1 - alpha) > values)
        data = data.loc[mask]

    return data


def _load(loader):
    data = loader()
    data.index = pd.to_datetime(data.index)
    return data


def clean(data: dict) -> pd.DataFrame:

    # Clean the data:
    clean_data = {}
    for (
        ship,
        loader,
    ) in data.items():
        logger.info(f"Cleaning: {ship}")

        try:
            clean_data[ship] = _clean(_load(loader))
        except KeyError as err:
            logger.warning(f"Failed to clean:{ship}\n {err}")
            continue

    return clean_data


def _clean(
    data: pd.DataFrame,
) -> pd.DataFrame:

    columns = data.columns[~data.isnull().all()]
    data_clean = data[columns]

    mask = (
        (-90 <= data["latitude"])
        & (data["latitude"] <= 90)
        & (0 <= data["longitude"])
        & (data["longitude"] <= 180)
    )

    data_clean = data_clean.loc[mask]
    data_clean = _quantile_clean(data_clean, columns=["latitude", "longitude"])
    data_clean = data_clean.fillna(method="backfill").fillna(method="ffill")

    return data_clean


def select_columns(data_clean: dict, data_descriptions: dict):

    # Assemble descriptions for all telematikenheter and ships:
    descriptions = {}
    for key, loader in data_descriptions.items():
        ship = Path(key).parts[0]
        telematikenhet = Path(key).parts[1]
        if not ship in descriptions:
            descriptions[ship] = {}
        descriptions[ship][telematikenhet] = loader()

    # select the data:
    data_selected = {}
    for (
        ship,
        loader,
    ) in data_clean.items():
        logger.info(f"Selecting columns: {ship}")

        data_selected[ship] = _select(
            data_clean=_load(loader), descriptions=descriptions[ship]
        )

    return data_selected


def _select(data_clean: pd.DataFrame, descriptions: dict) -> pd.DataFrame:

    rpm_columns = list(data_clean.columns[data_clean.columns.str.contains("RPM")])
    fuel_rate_columns = list(
        data_clean.columns[data_clean.columns.str.contains("FuelRate")]
    )
    speed_columns = list(data_clean.columns[data_clean.columns.str.contains("_SOG_")])
    cog_columns = list(data_clean.columns[data_clean.columns.str.contains("COGTrue")])

    data_clean["rpm"] = data_clean[rpm_columns].mean(axis=1)
    data_clean["fuel_rate"] = data_clean[fuel_rate_columns].sum(axis=1)
    data_new = data_clean.drop(columns=rpm_columns + fuel_rate_columns)

    counts = pd.Series(
        {key: description["count"] for key, description in descriptions.items()}
    )
    # Selecting speed and cog columns with the most data points (there are probably several GPS:s)

    # Mean speed cannot be above 25 m/s:
    mask = data_new[speed_columns].mean() > 25
    for key in data_new[data_new[speed_columns].columns[mask]]:
        speed_columns.remove(key)
        data_new.drop(columns=[key], inplace=True)

    speed_best = counts[speed_columns].idxmax()

    cog_best = counts[cog_columns].idxmax()

    data_new["sog"] = data_new[speed_best].copy()
    data_new["cog"] = data_new[cog_best].copy()
    data_new.drop(columns=speed_columns + cog_columns, inplace=True)

    # Clean a bit more...
    data_new = _quantile_clean(data_new, columns=["sog", "fuel_rate"])

    return data_new


def speed_select(data: dict, min_speed=0.05) -> dict:
    data_speed = {}
    for ship, loader in data.items():
        df_ = _load(loader)
        mask = df_["sog"] >= min_speed
        data_speed[ship] = df_.loc[mask].copy()

    return data_speed


def statistics(data: dict, resample_period: float) -> dict:
    """Statistics for each ship

    Parameters
    ----------
    data : dict
        _description_

    Returns
    -------
    dict
        _description_
    """

    ship_statistics = {}
    for (
        ship,
        loader,
    ) in data.items():
        logger.info(f"Statistics ship: {ship}")
        ship_statistics[ship] = _statistics(
            df=_load(loader), resample_period=resample_period
        )

    return ship_statistics


def _statistics(
    df: pd.DataFrame, resample_period: float, include_lat_lon_distance=True
) -> dict:

    stats = df.mean()

    stats["cog"] = np.rad2deg(
        np.arctan2(
            np.sin(np.deg2rad(df["cog"])).mean(), np.cos(np.deg2rad(df["cog"])).mean()
        )
    )

    stats["distance"] = scipy.integrate.simps(df["sog"], dx=resample_period)  # [m]
    stats["consumption"] = scipy.integrate.simps(
        df["fuel_rate"] / 3600, dx=resample_period
    )  # [m3]

    stats["time"] = len(df) * resample_period  # [s]
    stats["consumption per nautical mile"] = (
        stats["consumption"] / stats["distance"] * 1852 * 1000
    )  # [l/NM]
    stats["consumption per hour"] = (
        stats["consumption"] / stats["time"] * 3600 * 1000
    )  # [l/h]

    if include_lat_lon_distance:
        stats["distance lat lon"] = _lat_lon_distance(
            df=df
        )  # Distance from lat lon positions

    stats = stats.to_dict()
    # (units defined in data/08_reporting/units_statistics.yml)

    return stats


def _lat_lon_distance(df: pd.DataFrame, max_time_gap="10S"):

    data = geopandas.GeoDataFrame(
        df,
        geometry=geopandas.points_from_xy(df.longitude, df.latitude, crs="EPSG:4326"),
    )
    data = data.to_crs(epsg=3006)

    mask = np.concatenate(([True], (data.index[1:] - data.index[0:-1]) > max_time_gap))
    n_groups = mask.sum()
    data.loc[mask, "group"] = np.arange(0, n_groups)
    data["group"] = data["group"].ffill()
    distance = 0.0
    for group, df_group in data.groupby(by=["group"], sort=False):
        distance += df_group.distance(df_group.shift()).sum()

    return distance


def statistics_summary(ship_statistics: dict) -> dict:

    statistics_summary = pd.DataFrame()

    for (
        ship,
        loader,
    ) in ship_statistics.items():
        stats = pd.Series(loader(), name=ship)
        statistics_summary = statistics_summary.append(stats)

    statistics_summary.index.name = "ship"

    return statistics_summary


def datasets_tain(data: dict, exclude_ships=[]) -> dict:

    trains = {}
    df_all = pd.DataFrame()

    for ship, loader in data.items():

        if ship in exclude_ships:
            continue

        trains[ship] = loader()
        df = trains[ship].copy()
        df["ship"] = ship
        df["time"] = df.index
        df_all = df_all.append(df, ignore_index=True)

    trains["all"] = df_all

    return trains


def fit(trains: dict) -> dict:

    models = {}
    for ship, loader in trains.items():

        try:
            data = loader()  # From disk
        except:
            data = loader  # From memory

        models[ship] = _fit(data=data)

    return models


def _fit(data: pd.DataFrame) -> sklearn.base.BaseEstimator:

    y = data["fuel_rate"]
    X = data[["sog"]].copy()

    steps = [
        ("transformer", SplineTransformer(n_knots=4, degree=3)),
        ("estimator", Ridge(alpha=1e-3)),
    ]

    model = Pipeline(steps)

    grid = dict()
    grid["transformer__n_knots"] = [i for i in range(2, 5)]
    grid["transformer__degree"] = [i for i in range(10)]
    # perform the search

    cv = RepeatedKFold(n_splits=3, n_repeats=5, random_state=1)

    # define the grid search
    search = GridSearchCV(
        estimator=model,
        param_grid=grid,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
        cv=cv,
    )

    search_result = search.fit(X[["sog"]], y)
    model = search_result.best_estimator_
    model.fit(X[["sog"]], y)

    return model
