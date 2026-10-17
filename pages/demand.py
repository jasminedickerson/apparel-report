"""Demand page: is the shopper spending, and how much is just inflation?"""
import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from data import get_series, latest, real_sales, yoy
from components import kpi_card

dash.register_page(__name__, path="/", name="Demand", order=1,
                   title="Demand | The Apparel Report")

NOMINAL = "Nominal (current dollars)"
REAL = "Real (2015 dollars, apparel CPI-adjusted)"


def sales_long():
    """Nominal and real sales stacked: date, value, series. NaNs kept on purpose."""
    nominal = get_series("RSCCAS")
    nominal["series"] = NOMINAL
    real = real_sales()
    real["series"] = REAL
    return pd.concat([nominal, real])


def layout(**kwargs):
    sales = get_series("RSCCAS")
    sentiment = latest(get_series("UMCSENT"))
    saving = latest(get_series("PSAVERT"))

    # Latest month where BOTH nominal and real YoY exist, so they share one date
    both = (yoy(sales)
            .merge(yoy(real_sales()), on="date", suffixes=("_nom", "_real"))
            .dropna()
            .iloc[-1])

    first_year = int(sales["date"].dt.year.min())
    last_year = int(sales["date"].dt.year.max())

    return html.Div([
        html.H2("Is the shopper spending?"),

        html.Div([
            kpi_card("Clothing store sales, YoY",
                     f"{both['value_nom']:+.1%}",
                     f"{both['value_real']:+.1%} after price changes · "
                     f"{both['date']:%b %Y}"),
            kpi_card("Consumer sentiment (index)",
                     f"{sentiment['value']:.1f}", f"{sentiment['date']:%b %Y}"),
            kpi_card("Personal saving rate",
                     f"{saving['value']:.1f}%", f"{saving['date']:%b %Y}"),
        ], style={"display": "flex", "gap": "16px"}),

        dcc.Graph(id="demand-chart"),

        dcc.RangeSlider(
            id="demand-years",
            min=first_year, max=last_year, step=1,
            value=[first_year, last_year],
            marks={y: str(y) for y in range(first_year, last_year + 1, 5)},
        ),

        html.P("Real sales are an approximation: clothing store sales include "
               "some non-clothing items, and apparel CPI is a proxy deflator. "
               "The break in Oct 2025 reflects missing CPI data (government "
               "shutdown); it is not filled in.",
               style={"fontSize": "12px"}),
    ])


@callback(Output("demand-chart", "figure"), Input("demand-years", "value"))
def update_chart(years):
    start, end = years
    df = sales_long()
    df = df[df["date"].dt.year.between(start, end)]
    return px.line(
        df, x="date", y="value", color="series",
        title="Clothing & accessories store sales: nominal vs. real "
              "(monthly, seasonally adjusted)",
        labels={"date": "", "value": "Millions of dollars", "series": ""},
    )