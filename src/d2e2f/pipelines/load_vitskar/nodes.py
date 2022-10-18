"""
This is a boilerplate pipeline 'load_vitskar'
generated using Kedro 0.17.6
"""

import requests
import pandas as pd
from kedro.framework.session import get_current_session
from io import StringIO

import logging

log = logging.getLogger(__name__)

session = get_current_session()
context = session.load_context()
credentials = context._get_config_credentials()


def get_months(start: str, end: str) -> pd.DatetimeIndex:
    """The months between start and end as DatatimeIndex

    Parameters
    ----------
    start : str
        _description_
    end : str
        _description_

    Returns
    -------
    pd.DatetimeIndex
        _description_
    """

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    months = pd.date_range(start=start, end=end, freq="M")

    if len(months) > 0:

        if months[0] > start:
            months = months.insert(0, start)

        if months[-1] < end:
            months = months.append(pd.DatetimeIndex([end]))

    else:
        months = pd.DatetimeIndex([start, end])

    return months


def read_month(start: str, end: str, session: requests.Session) -> pd.DataFrame:
    """Read data between start and end

    Parameters
    ----------
    start : str
        _description_
    end : str
        _description_
    session : requests.Session
        _description_

    Returns
    -------
    str
        _description_
    """

    url = f"https://online.blueflow.se/be/external/raw/2?fromDate={start}&toDate={end}"
    log.info(f"requesting: {url}")
    r = session.get(url)
    s = r.content.decode("utf-8")
    df = pd.read_csv(StringIO(s))
    return df


def load_blueflow(start: str, end: str) -> dict:
    """Load all data between start and end month by month
    The result is return as a dictionary with data for each month

    Parameters
    ----------
    start : str
        _description_
    end : str
        _description_

    Returns
    -------
    dict
        _description_
    """

    months = get_months(start=start, end=end)
    months_str = [str(date) for date in months.date]

    files = {}

    assert "pass" in credentials, "define password as 'pass': in local/credentials.yml"
    password = credentials["pass"]
    assert "user" in credentials, "define password as 'user': in local/credentials.yml"
    user = credentials["user"]

    log.info(f"reading BlueFlow data between {start} and {end}")

    with requests.Session() as session:
        session.auth = (user, password)

        for i, month_str in enumerate(months_str[0:-1]):
            start_month = month_str
            end_month = months_str[i + 1]
            s_month = read_month(start=start_month, end=end_month, session=session)

            file_name = f"{start_month}--{end_month}"
            files[file_name] = s_month

    return files
