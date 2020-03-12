import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import requests
import pandas as pd

from app import app

column1 = dbc.Col(
    [
        dcc.Markdown(
            """

            # This is a map of recent earthquakes

            select from the drop down menu what period of time you would like
            to see earthquakes for.
            """
        ),
        html.Div([
            dcc.Dropdown(
                id='timeFrame',
                options=[
                    {'label': 'Last Quake', 'value': 'lastQuake'},
                    {'label': 'Last Hour', 'value': 'last/hour'},
                    {'label': 'Last Day', 'value': 'last/day'},
                    {'label': 'Last Week', 'value': 'last/week'},
                    {'label': 'Last Month', 'value': 'last/month'}
                ],
                value='lastQuake'
            ),
            html.Div(id='menuItems')
        ])
    ],
    md=2,
)

# fig = go.Figure()


@app.callback(
    dash.dependencies.Output('wheretheDataGoes', 'figure'),
    [dash.dependencies.Input('timeFrame', 'value')])
def update_output(value):
    data = requests.get(f'https://quake-ds-production.herokuapp.com/{value}')
    df = pd.DataFrame(data.json()['message']) if value != 'lastQuake' else \
        pd.DataFrame(data.json()['message'], index=[0])
    df['lat'] = df['lat'].apply(lambda x: str(x))
    df['lon'] = df['lon'].apply(lambda x: str(x))

    data = [
        go.Scattermapbox(
            lat=df['lat'],
            lon=df['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=14
            ),
            text=df['place'],
            hoverinfo='text'
        )
    ]

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=0,
                lon=0
            ),
            pitch=0,
            zoom=.5
        ),
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_layout(mapbox_style='stamen-terrain', height=700)
    return fig


column2 = dbc.Col([
    dcc.Graph(id='wheretheDataGoes'),
])

layout = dbc.Row([column1, column2], style={'margin-top': 100, 'height': 1000})
