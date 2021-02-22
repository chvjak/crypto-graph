#https://matplotlib.org/3.1.1/api/animation_api.html#module-matplotlib.animation

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import requests as r

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'b')

def init():
    #ax.set_xlim(0, 2*np.pi)
    #ax.set_ylim(-1, 1)
    return ln,

# for some reason it is slow
# BUG: looks like last point connected to first or something like that
def update(frame):
    global xdata, ydata

    ret = r.get("https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist")
    values = ret.json()
    trade_prices = [v[-1] for v in values]
    trade_times = [v[1] for v in values]

    sort_keys = [i for i in range(len(trade_times))]
    sort_keys.sort(key=lambda i: trade_times[i])
    
    trade_times = [trade_times[i] for i in sort_keys]
    trade_prices = [trade_prices[i] for i in sort_keys]

    xdata += trade_times
    ydata  += trade_prices
    ln.set_data(xdata, ydata)
    
    ax.relim()
    ax.autoscale_view()

    return ln,

ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 128), init_func=init, blit=True)
plt.show()
