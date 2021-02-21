import numpy as np
import matplotlib.pyplot as plt
import requests as r
import bisect as bs

def rescale_ob(ob_prices, ob_volumes, time_span_length, volume_per_time_unit):
    ps_up_volume = ob_volumes[:]            # prefix sum
    for i in range(len(ob_volumes) - 1):
        ps_up_volume[i + 1] += ps_up_volume[i]
    
    expected_volume = 0.0
    scaled_ob_prices = []
    for t in range(time_span_length):
        expected_volume += volume_per_time_unit
        ix = bs.bisect_right(ps_up_volume, expected_volume)
        if ix < len(ob_prices):
            scaled_ob_prices.append(ob_prices[ix])                           #price found by expected volume
        else:
            break
    return scaled_ob_prices

plt.show()
plt.autoscale()

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

    volume = sum([abs(v[-2]) for v in values])                                  # TODO: investigate if the trades are recorded twice - as SELL and as BUY - in this case the VOLUME is doubled
    time_span_length = x[-1] - x[0]
    volume_per_time_unit = volume / (x[-1] - x[0])                               # per second?

    plt.plot(x, y, 'b')
    ax = plt.axes()
    ax.set_facecolor('black')

    ret = r.get("https://api-pub.bitfinex.com/v2/book/tBTCUSD/P1")
    values = ret.json()
    up = [v[0] for v in values if v[-1] > 0]
    up_volume_list = [v[-1] for v in values if v[-1] > 0]

    down = [v[0] for v in values if v[-1] < 0]
    down_volume_list = [abs(v[-1]) for v in values if v[-1] < 0]

    scaled_up = rescale_ob(up, up_volume_list, time_span_length, volume_per_time_unit)
    scaled_down = rescale_ob(down, down_volume_list, time_span_length, volume_per_time_unit)

    step_up = 1
    step_down = 1

    plt.plot([x[-1] + step_up * i for i in range(len(scaled_up))], scaled_up, 'r')
    plt.plot([x[-1] + step_down * i for i in range(len(scaled_down))], scaled_down, 'g')

    plt.pause(0.005) # for better animation see https://matplotlib.org/3.1.1/api/animation_api.html#module-matplotlib.animation


