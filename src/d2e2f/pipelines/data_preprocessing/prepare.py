import pandas as pd
import numpy as np


def prepare(df_raw: pd.DataFrame, do_calculate_rudder_angles=False, renames={}):
    # df_raw = dataset.take(n_rows).to_pandas_dataframe()

    rename = {value: key for key, value in renames.items()}
    df = df_raw.rename(columns=rename)
    df.set_index("time", inplace=True)
    df.index = pd.to_datetime(df_raw.index)
    df.sort_index(inplace=True)
    df.index.name = "time"

    df["sog"] *= 1.852 / 3.6
    df = rename_columns(df)

    if do_calculate_rudder_angles:
        df = calculate_rudder_angles(df=df, drop=False)

    df.dropna(how="all", inplace=True, axis=1)  # remove columns with all NaN

    return df


def calculate_rudder_angles(df: pd.DataFrame, inplace=True, drop=False) -> pd.DataFrame:
    """Calculate "rudder angles" for the thrusters from cos/sin in the data files

    Parameters
    ----------
    df : pd.DataFrame
        data
    inplace : bool, optional
        [description], by default True

    Returns
    -------
    pd.DataFrame
        DataFrame with rudder angles added and cos/sin removed.
    """

    if inplace:
        df_ = df
    else:
        df_ = df.copy()

    for i in range(1, 5):
        sin_key = "sin_pm%i" % i
        cos_key = "cos_pm%i" % i
        delta_key = "delta_%i" % i

        df_[delta_key] = np.arctan2(df_[sin_key], -df_[cos_key])
        # df_[delta_key] = np.unwrap(df_[delta_key])

        if drop:
            df_.drop(columns=[sin_key, cos_key], inplace=True)

    return df_


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns of the data frame

    Parameters
    ----------
    df : pd.DataFrame
        raw data

    Returns
    -------
    pd.DataFrame
        data frame with columns with standard names
    """

    renames = {
        key: key.replace(" (kW)", "")
        .replace(" (deg)", "")
        .replace(" ()", "")
        .replace(" ", "_")
        .lower()
        for key in df.keys()
    }
    df_ = df.rename(columns=renames)

    # renames_power = {f"power_em_thruster_{i}": f"P{i}" for i in range(1, 5)}
    # renames_power["power_em_thruster_total"] = "P"
    # df_.rename(columns=renames_power, inplace=True)

    return df_
