import numpy as np
import matplotlib.pyplot as plt
import requests as r




plt.show()
plt.autoscale()
#plt.axis([min(x), max(x), min(y), max(y)])

while True:
    plt.clf()
    ret = r.get("https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist")
    values = ret.json()
    y = [v[-1] for v in values]
    x = [v[1] for v in values]
    sort_keys = [i for i in range(len(x))]
    sort_keys.sort(key=lambda i: x[i])
    x = [x[i] for i in sort_keys]
    y = [y[i] for i in sort_keys]

    plt.plot(x, y, 'b')
    ax = plt.axes()
    ax.set_facecolor('black')

    ret = r.get("https://api-pub.bitfinex.com/v2/book/tBTCUSD/P0")
    values = ret.json()
    up = [v[0] for v in values if v[-1] > 0]
    down = [v[0] for v in values if v[-1] < 0]

    step = 50000 #(max(x) - min(x)) / max([len(up), len(down)])

    plt.plot([x[-1] + step * i for i in range(len(up))], up, 'r')
    plt.plot([x[-1] + step * i for i in range(len(down))], down, 'g')

    plt.pause(0.005) # for better animation see https://matplotlib.org/3.1.1/api/animation_api.html#module-matplotlib.animation


