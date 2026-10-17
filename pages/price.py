"""Price page: is apparel inflation running hotter or cooler than overall?"""
import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from data import gap, get_series, latest, yoy
from components import kpi_card

dash.register_page(__name__, path="/price", name="Price", order = 2,
                   title="Price | The Apparel Report")

CATEGORIES = {
    "All items (headline)": "CPIAUCSL",
    "All apparel": "CPIAPPSL",
    "Men's & boys'": "CUSR0000SAA1",
    "Women's & girls'": "CUSR0000SAA2",
    "Footwear": "CUSR0000SEAE",
}

def category_yoy():
    """All categories stacked in long format: date, value, category."""
    frames = []
    for name, series_id in CATEGORIES.items():
        df = yoy(get_series(series_id))
        df["category"] = name
        frames.append(df)
    return pd.concat(frames).dropna()


def layout(**kwargs):
    apparel = yoy(get_series("CPIAPPSL"))
    all_items = yoy(get_series("CPIAUCSL"))
    a, t, g = latest(apparel), latest(all_items), latest(gap(apparel, all_items))

    return html.Div([
        html.H2("Are clothes getting pricier?"),

        html.Div([
            kpi_card("Apparel CPI, YoY", f"{a['value']:+.1%}", f"{a['date']:%b %Y}"),
            kpi_card("All-items CPI, YoY", f"{t['value']:+.1%}", f"{t['date']:%b %Y}"),
            kpi_card("Gap (apparel minus all items)",
                     f"{g['value'] * 100:+.1f} pts", f"{g['date']:%b %Y}"),
        ], style={"display": "flex", "gap": "16px"}),

        dcc.Checklist(
            id="price-categories",
            options=list(CATEGORIES),
            value=list(CATEGORIES),
            inline=True,
            style={"marginTop": "16px"},
        ),

        dcc.Graph(id="price-chart"),
    ])


@callback(Output("price-chart", "figure"), Input("price-categories", "value"))
def update_chart(selected):
    df = category_yoy()
    df = df[df["category"].isin(selected)]
    fig = px.line(
        df, x="date", y="value", color="category",
        title="Year-over-year price change by category (CPI, seasonally adjusted)",
        labels={"date": "", "value": "YoY price change", "category": ""},
    )
    fig.add_hline(y=0, line_width=1, line_color="gray")
    fig.update_yaxes(tickformat=".0%")
    fig.update_traces(line=dict(dash="dash", color="gray"),
                    selector=dict(name="All items (headline)"))
    return fig