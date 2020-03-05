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

            ## This is a map of recent earthquakes

            select from the drop down menu what period of time you would like
            to see earthquakes for.
            """
        ),
    ],
    md=2,
)


data = requests.get('https://quake-ds-production.herokuapp.com/last/day')
df = pd.DataFrame(data.json()['message'])

df['lat'] = df['latitude'].apply(lambda x: str(x))
df['lon'] = df['longitude'].apply(lambda x: str(x))

data = [
    go.Scattermapbox(
        lat=df['lat'],
        lon=df['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        text=df['place'],
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
        zoom=1
    ),
)

fig = go.Figure(data=data, layout=layout)

fig.update_layout(mapbox_style='stamen-terrain')

column2 = dbc.Col([
    dcc.Graph(figure=fig),
])

layout = dbc.Row([column1, column2])
