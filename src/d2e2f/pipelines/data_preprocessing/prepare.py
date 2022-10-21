import pandas as pd
import numpy as np
import re


def prepare(
    df_raw: pd.DataFrame,
    P_max: float = None,
    do_calculate_rudder_angles=False,
    renames={},
):
    # df_raw = dataset.take(n_rows).to_pandas_dataframe()

    df = df_raw.rename(columns=renames)
    df = rename_columns(df, rename=renames)

    # Calculate Power if missing from engine load
    for i in range(4):
        if (not f"P{i+1}" in df) and (f"Engine load ME{i+1} (%)" in df):
            if P_max is None:
                raise ValueError("Please specify P_max so that power can be calculated")
            df[f"P{i+1}"] = df[f"Engine load ME{i+1} (%)"] * P_max

    if not "P" in df:

        regexp = re.compile(r"P\d+$")

        P_columns = []
        for column in df.columns:
            if regexp.search(column):
                P_columns.append(column)

        if len(P_columns) > 0:
            df["P"] = df[P_columns].sum(axis=1)

    # Add consumptions
    consumption_columns = [
        f"Consumption ME{i+1} (L/h)"
        for i in range(4)
        if f"Consumption ME{i+1} (L/h)" in df
    ]
    if len(consumption_columns) > 0:
        df["consumption"] = df[consumption_columns].sum(axis=1)

    check_data(df=df)

    df.set_index("time", inplace=True)
    df.index = pd.to_datetime(df.index)
    mask = df.index.duplicated(keep="first")
    df = df.loc[~mask].copy()
    df.sort_index(inplace=True)
    df.index.name = "time"

    df["sog"] *= 1.852 / 3.6

    # mask = df["sog"] > min_speed
    # df = df.loc[mask].copy()

    if do_calculate_rudder_angles:
        if "delta1" in df:
            for i in range(1, 5):
                delta_key = f"delta{i}"
                if not delta_key in df:
                    break

                df[f"sin_pm{i}"] = np.sin(df[delta_key])
                df[f"cos_pm{i}"] = np.cos(df[delta_key])

        else:
            df = calculate_rudder_angles(df=df, drop=False)

    df.dropna(how="all", inplace=True, axis=1)  # remove columns with all NaN

    return df


def check_data(df):

    mandatory_columns = [
        "time",
        "sog",
        "latitude",
        "longitude",
    ]

    missing = set(mandatory_columns) - set(df.columns)
    assert len(missing) == 0, f"The following columns are missing: {missing}"


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


def rename_columns(df: pd.DataFrame, rename={}) -> pd.DataFrame:
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

    renames1 = {
        key: key.replace(" (kW)", "")
        .replace(" (deg)", "")
        .replace(" ()", "")
        .replace(" ", "_")
        for key in df.keys()
    }

    renames = {
        key.lower(): value for key, value in renames1.items() if not key in rename
    }

    df_ = df.rename(columns=renames)

    # renames_power = {f"power_em_thruster_{i}": f"P{i}" for i in range(1, 5)}
    # renames_power["power_em_thruster_total"] = "P"
    # df_.rename(columns=renames_power, inplace=True)

    return df_


def redefine_heading(df: pd.DataFrame) -> pd.Series:
    """The double ended ferry is run in reverse direction half of the time.
    This means that the "heading" measures by the compas is 180 degrees wrong, compared to course over ground from GPS.
    This method makes this 180 degrees heading shift whenever needed.

    Parameters
    ----------
    trip : pd.DataFrame
        [description]

    Returns
    -------
    pd.Series
        corrected heading
    """

    trips = df.groupby(by="trip_no")

    for trip_no, trip in trips:

        heading = trip["heading"]
        cog = trip["cog"]

        if (cog - heading).abs().mean() > 90:
            df.loc[trip.index, "heading"] = np.mod(heading + 180, 360)
            df.loc[trip.index, "reversing"] = True
        else:
            df.loc[trip.index, "reversing"] = False

    return df
