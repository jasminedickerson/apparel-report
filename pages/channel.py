"""Channel page: where are people buying, and how has that shifted?"""
import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from data import get_series, index_to, latest, yoy
from components import kpi_card

dash.register_page(__name__, path="/channel", name="Channel", order=3,
                   title="Channel | The Apparel Report")

CHANNELS = {
    "Online & nonstore": "RSNSR",
    "Department stores": "RSDSELD",
    "Clothing stores": "RSCCAS",
}


def channel_index():
    """All channels stacked in long format: date, value, channel."""
    frames = []
    for name, series_id in CHANNELS.items():
        df = index_to(get_series(series_id))
        df["channel"] = name
        frames.append(df)
    return pd.concat(frames).dropna()


def layout(**kwargs):
    cards = []
    for name, series_id in CHANNELS.items():
        row = latest(yoy(get_series(series_id)))
        cards.append(kpi_card(f"{name}, sales YoY",
                              f"{row['value']:+.1%}",
                              f"{row['date']:%b %Y}"))

    return html.Div([
        html.H2("Where people shop"),
        html.Div(cards, style={"display": "flex", "gap": "16px"}),

        dcc.Checklist(
            id="channel-picks",
            options=list(CHANNELS),
            value=list(CHANNELS),
            inline=True,
            style={"marginTop": "16px"},
        ),

        dcc.Graph(id="channel-chart"),
    ])


@callback(Output("channel-chart", "figure"), Input("channel-picks", "value"))
def update_chart(selected):
    df = channel_index()
    df = df[df["channel"].isin(selected)]
    fig = px.line(
        df, x="date", y="value", color="channel",
        title="Retail sales by channel, indexed (2015 = 100, seasonally adjusted)",
        labels={"date": "", "value": "Index (2015 = 100)", "channel": ""},
    )
    fig.add_hline(y=100, line_width=1, line_color="gray")
    return fig