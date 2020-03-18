import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import requests
import pandas as pd
import numpy as np

from app import app

column1 = dbc.Col(
    [
        dcc.Markdown(
            """

            ## Recent Earthquakes
            The map at the right shows the recent earthquakes. Larger dots are
            larger earthquakes.

            Use the drop down menu what period of time you would like
            to see earthquakes for.

            You can adjust for minimum magnitude using the slider below

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
        ]),
        html.Div([
            dcc.Markdown("\n"),
            dcc.Slider(
                id='magnitude',
                min=0,
                max=10,
                step=.5,
                value=5.5
            ),
            dcc.Markdown(id='sliderOutput')
        ])
    ],
    md=2,
)

# fig = go.Figure()
@app.callback(
    dash.dependencies.Output('sliderOutput', 'children'),
    [dash.dependencies.Input('magnitude', 'value')])
def display_min_mag(mag_num):
    return f"#### Minimum Magnitude {mag_num}"

@app.callback(
    dash.dependencies.Output('wheretheDataGoes', 'figure'),
    [dash.dependencies.Input('timeFrame', 'value'),
     dash.dependencies.Input('magnitude', 'value')])
def update_output(value, mag):
    data = requests.get(f'https://quake-ds-staging.herokuapp.com/{value}/{float(mag)}')
    print(data.text)
    if type(data.json()['message']) == type({1:'a'}):
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
                    size=df['mag'] + 9
                ),
                text=df[['place', 'time']],
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
    else:
        data = [
            go.Scattermapbox(
                lat=[0],
                lon=[0],
                mode='text',
                text=[f"No Quakes Above {mag} available to show"],
                textposition='middle center'
            )
        ]

        layout = go.Layout(
            autosize=True,
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
