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

def gap(a, b):
    """a minus b on matching dates (e.g., apparel YoY minus all-items YoY)."""
    merged = a.merge(b, on="date", suffixes=("_a", "_b"))
    out = merged[["date"]].copy()
    out["value"] = merged["value_a"] - merged["value_b"]
    return out

def index_to(df, year=2015):
    """Rebase a series so the chosen year's average = 100."""
    base = df.loc[df["date"].dt.year == year, "value"].mean()
    out = df.copy()
    out["value"] = out["value"] / base * 100
    return out

def real_sales():
    """Clothing store sales in 2015 dollars, deflated by apparel CPI.

    Left merge keeps every sales month. Months with no CPI value
    (like Oct 2025) stay as NaN, so the chart shows an honest break.
    """
    sales = get_series("RSCCAS")
    cpi = index_to(get_series("CPIAPPSL"))  # 2015 = 100
    merged = sales.merge(cpi, on="date", how="left", suffixes=("_sales", "_cpi"))
    out = merged[["date"]].copy()
    out["value"] = merged["value_sales"] / (merged["value_cpi"] / 100)
    return out