import numpy as np


def apparent_wind_to_true(sog, aw, awa):
    return np.sqrt(aw ** 2 + sog ** 2 - 2 * aw * sog * np.cos(awa))


def apparent_wind_angle_to_true(sog, aw, awa):
    return np.arccos(
        (aw * np.cos(awa) - sog)
        / np.sqrt(aw ** 2 + sog ** 2 - 2 * aw * sog * np.cos(awa))
    )
