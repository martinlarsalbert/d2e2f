import pandas as pd
import statsmodels.api as sm


def fit(df: pd.DataFrame):

    y = df.pop("P")
    X = pd.DataFrame()
    X["sog**3"] = df["sog**3"]
    X["aw_x**2*sog"] = df["aw_x**2*sog"]
    if "beta**2*sog" in df:
        X["beta**2*sog"] = df["beta**2*sog"]

    model = sm.OLS(y, X)
    results = model.fit()

    return results
