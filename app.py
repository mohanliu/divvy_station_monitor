import dash
import dash_core_components as dcc
import dash_html_components as html
import requests, json, os
import pandas as pd
from plotly import graph_objects as go
import numpy as np

QUERY_FUNC = os.environ.get('divvy_cloud_function')
mapbox_access_token = os.environ.get('mapbox_token')

def to_dataframe(raw):
    lst_of_lst = [v.split(',') for v in raw.split('\n')]
    df = pd.DataFrame(lst_of_lst, columns=['timestamp', 'stationid', 'bikes_avail', 'docks_avail'])
    return df

external_stylesheets = ['static/css/bWLwgP.css']
external_scripts = []

class CustomDash(dash.Dash):
    def interpolate_index(self, verbose=False, **kwargs):
        # Inspect the arguments by printing them
        if verbose:
            print(kwargs)

        return '''
        <!DOCTYPE html>
        <html>
            <head>
                <title>DivvyStationMonitor</title>
            </head>
            <body bgcolor='#111111'>
                {app_entry}
                {config}
                {scripts}
                {renderer}
            </body>
        </html>
        '''.format(
            app_entry=kwargs['app_entry'],
            config=kwargs['config'],
            scripts=kwargs['scripts'],
            renderer=kwargs['renderer'])

app = CustomDash(external_stylesheets=external_stylesheets,
                external_scripts=external_scripts,
                meta_tags=[
                        # A description of the app, used by e.g.
                        # search engines when displaying search results.
                        {
                            'name': 'Divvy Station Monitor',
                            'content': 'Divvy Station Monitor'
                        },
                        # A tag that tells Internet Explorer (IE)
                        # to use the latest renderer version available
                        # to that browser (e.g. Edge)
                        {
                            'http-equiv': 'X-UA-Compatible',
                            'content': 'IE=edge'
                        },
                        # A tag that tells the browser not to scale
                        # desktop widths to fit mobile screens.
                        # Sets the width of the viewport (browser)
                        # to the width of the device, and the zoom level
                        # (initial scale) to 1.
                        #
                        # Necessary for "true" mobile support.
                        {
                          'name': 'viewport',
                          'content': 'width=device-width, initial-scale=1.0'
                        }
                    ]
            )

server = app.server

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

stationdata = pd.read_csv('data/station.csv')

app.layout = html.Div(style={'backgroundColor': colors['background'], "height" : "100vh", 'width': '100vw'}, children=[
    html.Div(
            [  
                html.P("Divvy Station Monitor", 
                        style={
                        'textAlign': 'center',
                        'font-size': 30,
                        'font-weight': 600,
                        'color': colors['text'],
                        'width': '95%',
                        'display': 'inline-block',
                        'margin-bottom': '0px',
                        'padding-bottom': '0px',
                        'margin-top': '5px',
                    }),
                html.A('About', href='static/html/about.html', target="_blank", 
                    style={
                        'width': '5%', 
                        'display': 'inline-block',
                        'color': 'white',
                        'font-style': 'italic',
                        }),
            ],
        ),
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            config={'displayModeBar': False},
            figure={
                'data': [   
                    go.Scattermapbox(
                        lat=list(np.array(stationdata.lat)),
                        lon=list(np.array(stationdata.lon)),
                        customdata=list(map(lambda x: str(x), np.array(stationdata.station_id))),
                        text=['<b>Station ID</b>: {}<br><b>Capacity</b>: {}<br><b>(Lat, Lon)</b>: ({:.3f}, {:.3f})<br><b>Name</b>: {}'\
                                .format(sid, cap, lon, lat, name) 
                                for (sid, cap, lon, lat, name) in zip(
                                    stationdata.station_id, 
                                    stationdata.capacity,
                                    stationdata.lon,
                                    stationdata.lat,
                                    stationdata.name
                                    )
                                ],
                        mode='markers',
                        hoverinfo = 'text',
                        marker=go.scattermapbox.Marker(
                            size=20,
                            color='blue',
                            opacity=0.5
                        ),   
                        visible=True,
                        name='Map',
                        showlegend=False,
                    ),
                ],
                'layout': {
                    'height': 750,
                    'autosize': True,
                    'paper_bgcolor': colors['background'],
                    'mapbox': go.layout.Mapbox(
                            accesstoken=mapbox_access_token,
                            center=go.layout.mapbox.Center(
                                lat=41.869, 
                                lon=-87.629
                            ),
                            pitch=60,
                            zoom=14,
                            style = 'outdoors',
                        ),
                    'clickmode': 'event+select',
                    'margin': {'l': 30, 'b': 15, 'r': 30, 't': 5},
                },
            },
        )
    ], 
        style={'width': '49vw', 'display': 'inline-block', 'padding': '0 20'},
    ),
    html.Div(children=[
        dcc.Dropdown(
            options=[
                {'label': 'Number of Bikes', 'value': 'bikes_avail'},
                {'label': 'Number of Docks', 'value': 'docks_avail'},
            ],
            value='bikes_avail',
            clearable=False,
            id='control_panel', style={'max-height': '1vh', 'width': '50%', 'float': 'right', 'margin-bottom': '5px'}
        ), 
        dcc.Graph(id='day-time-series', style={'margin-top': '10vh', 'max-height': '40vh'}, config={'displayModeBar': False}),
        dcc.Graph(id='week-time-series', style={'margin-top': '2vh', 'max-height': '40vh'}, config={'displayModeBar': False}),
    ], style={'display': 'inline-block', 'min-width': '49vw'}),
])

def create_time_series(dff, colname, line_color, mode, title, anno):
    return {
        'data': [go.Scatter(
            x=pd.to_datetime(dff['timestamp']).dt.tz_localize('utc').dt.tz_convert('US/Central'),
            y=dff[colname],
            mode=mode, 
            line_color=line_color,
        )],
        'layout': {
            'title': {
                'text': title,
                'font': dict(
                    family='Open Sans, sans-serif',
                    size=18,
                    color='white'
                ),
             },
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                    'color': colors['text']
                },
            # 'height': 300,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 30},
            'xaxis': {'showgrid': True},
            'xaxis_rangeslider_visible': True,
            'annotations' : [dict( x=0,
                        y=1,
                        xanchor='left',
                        yanchor='bottom',
                        xref="paper", yref="paper",
                        text=anno,
                        font=dict(color='white', size=18, family='Open Sans, sans-serif', ),
                        ax=0, ay=0),]
        }
    }

def create_time_series_with_bound(dff, colname_pre, line_color, mode, title, anno):
    return {
        'data': [
            go.Scatter(
                x=dff.timeindex,
                y=dff[colname_pre+'_ave'],
                name='Ave',
                mode=mode, 
                line_color=line_color,
            ),
            go.Scatter(
                x=dff.timeindex,
                y=dff[colname_pre+'_max'],
                name='Max',
                mode='lines',
                line=dict(width=0),
                fillcolor='rgba(200, 100, 200, 0.3)',
                fill='tonexty' 
            ),
            go.Scatter(
                x=dff.timeindex,
                y=dff[colname_pre+'_min'],
                mode='lines',
                line=dict(width=0),
                name='Min',
                fillcolor='rgba(200, 100, 200, 0.3)',
                fill='tonexty' 
            )

            ],
        'layout': {
            'title': {
                'text': title,
                'font': dict(
                    family='Open Sans, sans-serif',
                    size=18,
                    color='white'
                ),
             },
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                    'color': colors['text']
                },
            # 'height': 300,
            'showlegend': False,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 30},
            'xaxis': {'showgrid': True},
            'xaxis_rangeslider_visible': True,
            'annotations' : [dict( x=0,
                        y=1,
                        xanchor='left',
                        yanchor='bottom',
                        xref="paper", yref="paper",
                        text=anno,
                        font=dict(color='white', size=18, family='Open Sans, sans-serif', ),
                        ax=0, ay=0),]
        }
    }


@app.callback(
    dash.dependencies.Output('week-time-series', 'figure'),
    [
        dash.dependencies.Input('crossfilter-indicator-scatter', 'clickData'),
        dash.dependencies.Input('control_panel', 'value'),
    ])
def update_lastweek_timeseries(clickData, value):
    try:
        stid = clickData['points'][0]['customdata']
    except:
        stid = '192'
    reslst = requests.post(QUERY_FUNC, json={'stationid':stid}).content.decode('utf-8')
    df = to_dataframe(reslst)

    df['timeindex'] = pd.to_datetime(df['timestamp']).dt.tz_localize('utc').dt.tz_convert('US/Central')
    df['month'] = df.timeindex.apply(lambda x: x.month)
    df['day'] = df.timeindex.apply(lambda x: x.day)
    df['hour'] = df.timeindex.apply(lambda x: x.hour)

    df.bikes_avail = df.bikes_avail.astype('int')
    df.docks_avail = df.docks_avail.astype('int')

    min_df = df.groupby(['month', 'day', 'hour'])[['timeindex', 'bikes_avail', 'docks_avail']].min()\
            .reset_index().rename(columns={"bikes_avail": "bikes_avail_min", "docks_avail": "docks_avail_min"})

    max_df = df.groupby(['month', 'day', 'hour'])[['bikes_avail', 'docks_avail']].max()\
        .reset_index().rename(columns={"bikes_avail": "bikes_avail_max", "docks_avail": "docks_avail_max"})

    ave_df = df.groupby(['month', 'day', 'hour'])[['bikes_avail', 'docks_avail']].mean()\
        .reset_index().rename(columns={"bikes_avail": "bikes_avail_ave", "docks_avail": "docks_avail_ave"})

    final_df = min_df.merge(max_df, on=['month', 'day', 'hour']).merge(ave_df, on=['month', 'day', 'hour'])

    return create_time_series_with_bound(final_df, value, 'deepskyblue', 'lines', 'Last Week (<i>per hour</i>)', '')


@app.callback(
    dash.dependencies.Output('day-time-series', 'figure'),
    [
        dash.dependencies.Input('crossfilter-indicator-scatter', 'clickData'),
        dash.dependencies.Input('control_panel', 'value'),
    ])
def update_lastday_timeseries(clickData, value):
    try:
        stid = clickData['points'][0]['customdata']
    except:
        stid = '192'
    reslst = requests.post(QUERY_FUNC, json={'stationid':stid}).content.decode('utf-8')
    df = to_dataframe(reslst)
    return create_time_series(df.iloc[-288:], value, 'orange', 'lines', 'Last 24 Hours (<i>per 5 mins</i>)', "Station "+stid)

if __name__ == '__main__':
    app.run_server(debug=True)
