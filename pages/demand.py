import dash
from dash import html, dcc, callback, Input, Output
import plotly.express as px

from data import get_series, latest, yoy

dash.register_page(__name__, path="/", name="Demand", order = 1,
                   title="Demand | The Apparel Report")


def kpi_card(label, value_text, date):
    return html.Div([
        html.P(label),
        html.H2(value_text),
        html.P(f"{date:%b %Y}"),
    ], style={"border": "1px solid #ccc", "padding": "12px", "flex": "1"})


def layout(**kwargs):
    sales = get_series("RSCCAS")
    sentiment = latest(get_series("UMCSENT"))
    saving = latest(get_series("PSAVERT"))
    sales_yoy = latest(yoy(sales))

    first_year = int(sales["date"].dt.year.min())
    last_year = int(sales["date"].dt.year.max())

    return html.Div([
        html.H2("Is the shopper spending?"),

        html.Div([
            kpi_card("Clothing store sales, YoY",
                     f"{sales_yoy['value']:+.1%}", sales_yoy["date"]),
            kpi_card("Consumer sentiment (index)",
                     f"{sentiment['value']:.1f}", sentiment["date"]),
            kpi_card("Personal saving rate",
                     f"{saving['value']:.1f}%", saving["date"]),
        ], style={"display": "flex", "gap": "16px"}),

        dcc.Graph(id="demand-chart"),

        dcc.RangeSlider(
            id="demand-years",
            min=first_year, max=last_year, step=1,
            value=[first_year, last_year],
            marks={y: str(y) for y in range(first_year, last_year + 1, 5)},
        ),
    ])


@callback(Output("demand-chart", "figure"), Input("demand-years", "value"))
def update_chart(years):
    start, end = years
    df = get_series("RSCCAS")
    df = df[df["date"].dt.year.between(start, end)]
    return px.line(
        df, x="date", y="value",
        title="Clothing & accessories store sales (monthly, seasonally adjusted)",
        labels={"date": "", "value": "Millions of dollars"},
    )