"""Reusable layout pieces shared across pages."""
from dash import html


def kpi_card(label, value_text, note):
    return html.Div([
        html.P(label),
        html.H2(value_text),
        html.P(note),
    ], style={"border": "1px solid #ccc", "padding": "12px", "flex": "1"})