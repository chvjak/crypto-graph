#https://matplotlib.org/3.1.1/api/animation_api.html#module-matplotlib.animation

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import requests as r
import Utils as u
from collections import deque 

fig, ax = plt.subplots()

MAX_TRADE_LEN = 300
xdata = deque(maxlen = MAX_TRADE_LEN ) 
ydata = deque(maxlen = MAX_TRADE_LEN ) 
ln, = plt.plot([], [], 'b')

def init():
    #ax.set_xlim(0, 2*np.pi)
    #ax.set_ylim(-1, 1)
    return ln,

# for some reason it is slow
# BUG: looks like last point connected to first or something like that
def update(frame):
    global xdata, ydata


    trade_prices, trade_volumes, trade_times = u.load_trades(xdata[-1] if len(xdata) else 0)
    xdata += trade_times
    ydata  += trade_prices

    ln.set_data(xdata, ydata)
    
    ax.relim()
    ax.autoscale_view()

    return ln,

ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 128), init_func=init, blit=True)
plt.show()
