# hthis one: dash + plotly
# https://www.geeksforgeeks.org/plot-live-graphs-using-python-dash-and-plotly/amp/

# quite verbose but flask+chartjs
# https://medium.com/@data.corgi9/real-time-graph-using-flask-75f6696deb55
# https://towardsdatascience.com/flask-and-chart-js-tutorial-i-d33e05fba845

import dash 
from dash.dependencies import Output, Input
import dash_core_components as dcc 
import dash_html_components as html 
import plotly 
import random 
import plotly.graph_objs as go 
from collections import deque 
import requests as r


X = deque(maxlen = 20) 
X.append(1) 
Y = deque(maxlen = 20) 
Y.append(1) 

app = dash.Dash(__name__) 
app.layout = html.Div( 
    [ 
        dcc.Graph(id = 'live-graph', animate = True), 
        dcc.Interval( 
            id = 'graph-update', 
            interval = 1000, 
            n_intervals = 0
        ), 
    ] 
) 

@app.callback(Output('live-graph', 'figure'), [ Input('graph-update', 'n_intervals') ]) 
def update_graph_scatter(n): 
    global X
    global Y

    ret = r.get("https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist")
    values = ret.json()
    trade_prices = [v[-1] for v in values]
    trade_times = [v[1] for v in values]

    sort_keys = [i for i in range(len(trade_times))]
    sort_keys.sort(key=lambda i: trade_times[i])
    
    trade_times = [trade_times[i] for i in sort_keys]
    trade_prices = [trade_prices[i] for i in sort_keys]

    X += trade_times
    Y += trade_prices

    data = go.Scatter( 
            x=list(X), 
            y=list(Y), 
            name='Scatter', 
            mode= 'lines+markers'
    ) 

    return {'data': [data], 'layout' : go.Layout(xaxis = dict(range = [min(X), max(X)]), yaxis = dict(range = [min(Y), max(Y)]),)} 

if __name__ == '__main__': 
    app.run_server()