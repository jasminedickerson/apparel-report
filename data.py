"""Shared data loading and calculations for The Apparel Report."""
import io
import time
from functools import lru_cache

import pandas as pd
import requests

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
TRIES = 3


@lru_cache(maxsize=None)
def _download(series_id):
    """Download one FRED series once; later calls reuse the cached copy."""
    url = FRED_URL.format(series_id)
    for attempt in range(1, TRIES + 1):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            break
        except requests.RequestException as err:
            print(f"{series_id}: try {attempt} failed ({err})")
            if attempt == TRIES:
                raise
            time.sleep(1)

    df = pd.read_csv(io.StringIO(response.text), na_values=".")
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    time.sleep(1)  # polite pause between series
    return df


def get_series(series_id):
    """Return a fresh copy so no page can accidentally change the cache."""
    return _download(series_id).copy()


def yoy(df):
    """Year-over-year change: value / value 12 months ago - 1."""
    out = df.copy()
    out["value"] = out["value"] / out["value"].shift(12) - 1
    return out


def latest(df):
    """Most recent non-missing row (handles NaN months like Oct 2025 CPI)."""
    return df.dropna().iloc[-1]