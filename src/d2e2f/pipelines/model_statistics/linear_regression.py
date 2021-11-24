import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression


def label(df: pd.DataFrame):
    y = df.pop("P")
    return y


def features(df: pd.DataFrame):

    X = pd.DataFrame()
    X["sog**3"] = df["sog**3"]
    X["aw_x**2*sog"] = df["aw_x**2*sog"]
    if "beta**2*sog" in df:
        X["beta**2*sog"] = df["beta**2*sog"]

    return X


def fit(df: pd.DataFrame):

    X = features(df=df)
    y = label(df=df)

    # model = sm.OLS(y, X)
    # results = model.fit()
    model = LinearRegression()
    model.fit(X=X, y=y)

    return model
