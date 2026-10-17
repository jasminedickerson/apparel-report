import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
server = app.server  # needed later for deployment

app.layout = html.Div([
    html.Header([
        html.H1("The Apparel Report"),
        html.Nav([
            dcc.Link(page["name"], href=page["relative_path"],
                     style={"marginRight": "16px"})
            for page in dash.page_registry.values()
        ]),
    ]),
    html.Hr(),
    dash.page_container,
    html.Hr(),
    html.Footer([
        html.P("Source: Federal Reserve Bank of St. Louis (FRED); "
               "U.S. Census Bureau; U.S. Bureau of Labor Statistics; "
               "U.S. Bureau of Economic Analysis."),
        html.P("Consumer sentiment: University of Michigan, Surveys of "
               "Consumers. © University of Michigan."),
        html.P("Latest retail sales month is preliminary."),
    ], style={"fontSize": "12px"}),
])

if __name__ == "__main__":
    app.run(debug=True)