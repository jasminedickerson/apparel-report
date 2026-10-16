import io
import time

import pandas as pd
import requests

BASE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

SERIES = {
    # Demand
    "RSCCAS":        "Clothing store sales",
    "UMCSENT":       "Consumer sentiment",
    "PSAVERT":       "Personal saving rate",
    # Price
    "CPIAPPSL":      "Apparel CPI",
    "CPIAUCSL":      "All-items CPI",
    "CUSR0000SAA2":  "Women's & girls' apparel CPI",
    "CUSR0000SAA1":  "Men's & boys' apparel CPI",
    "CUSR0000SEAE":  "Footwear CPI",
    "CUSR0000SEAF":  "Infants' & toddlers' apparel CPI",
    # Channel
    "RSNSR":         "Online & nonstore sales",
    "SM4522USS":     "Department store sales",
}


def load_series(series_id, tries=3):
    """Download one FRED series and return a clean two-column table."""
    url = BASE_URL + series_id
    for attempt in range(1, tries + 1):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            break
        except requests.RequestException:
            if attempt == tries:
                raise
            time.sleep(3)

    df = pd.read_csv(io.StringIO(response.text), na_values=".")
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


for series_id, label in SERIES.items():
    try:
        df = load_series(series_id)
        latest = df.dropna().iloc[-1]
        missing = df["value"].isna().sum()
        print(f"OK    {series_id:<14} {label:<34} "
              f"{latest['date']:%Y-%m}  {latest['value']:>10,.1f}  "
              f"missing: {missing}")
    except Exception as e:
        print(f"FAIL  {series_id:<14} {label:<34} {e}")
    time.sleep(1)

# Confirm the shutdown gap in apparel CPI
apparel = load_series("CPIAPPSL")
oct_2025 = apparel[apparel["date"] == "2025-10-01"]
print("\nCPIAPPSL Oct 2025:", oct_2025["value"].tolist())