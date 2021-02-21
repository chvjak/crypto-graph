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
#plt.autoscale()
#axes = plt.gca()
#axes.set_ylim((55000, 60000))

ax = plt.axes()


trade_prices = []
trade_times = []
trade_volumes = []

while True:

    plt.clf()
    plt.grid(b = True, c="w")
    ret = r.get("https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist")
    values = ret.json()
    trade_prices += [v[-1] for v in values]
    trade_times += [v[1] for v in values]
    trade_volumes += [abs(v[-2]) for v in values]
    trade_volumes1 = [v[-2] for v in values]
    sort_keys = [i for i in range(len(trade_times))]
    sort_keys.sort(key=lambda i: trade_times[i])
    
    trade_times = [trade_times[i] for i in sort_keys]
    trade_prices = [trade_prices[i] for i in sort_keys]
    trade_volumes = [trade_volumes [i] for i in sort_keys]
    trade_volumes1 = [trade_volumes1 [i] for i in sort_keys]

    max_volume = max(trade_volumes)
    min_volume = min(trade_volumes)
    volume = sum(trade_volumes)                                  # TODO: investigate if the trades are recorded twice - as SELL and as BUY - in this case the VOLUME is doubled
    
    time_span_length = trade_times[-1] - trade_times[0]
    volume_per_time_unit = volume / (trade_times[-1] - trade_times[0])                               # per second?

    plt.plot(trade_times, trade_prices, 'b')
    volume_color_values = [100 + int(155 / (max_volume - min_volume) * v) for v in trade_volumes]
    volume_colors = ['#%02x0000' % v for v in volume_color_values]

    plt.scatter(trade_times, trade_prices, c=volume_colors)
    ax = plt.axes()
    ax.set_facecolor('black')
    #ax.set(ylim=(57600, 57900))

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

    plt.plot([trade_times[-1] + step_up * i for i in range(len(scaled_up))], scaled_up, 'r')
    plt.plot([trade_times[-1] + step_down * i for i in range(len(scaled_down))], scaled_down, '#00FF00')

    plt.pause(0.005) # for better animation see https://matplotlib.org/3.1.1/api/animation_api.html#module-matplotlib.animation


