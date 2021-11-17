import pandas as pd
import numpy as np


def prepare(
    df_raw: pd.DataFrame, do_calculate_rudder_angles=False, min_speed=0.01, renames={}
):
    # df_raw = dataset.take(n_rows).to_pandas_dataframe()

    rename = {value: key for key, value in renames.items()}
    df = df_raw.rename(columns=rename)
    df["P"] = df[[f"P{i+1}" for i in range(4)]].sum(axis=1)
    check_data(df=df)

    df.set_index("time", inplace=True)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df.index.name = "time"

    df["sog"] *= 1.852 / 3.6

    mask = df["sog"] > min_speed
    df = df.loc[mask].copy()

    df = rename_columns(df, rename=rename)

    if do_calculate_rudder_angles:
        df = calculate_rudder_angles(df=df, drop=False)

    df.dropna(how="all", inplace=True, axis=1)  # remove columns with all NaN

    return df


def check_data(df):

    mandatory_columns = [
        "time",
        "P",
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
