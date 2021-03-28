import numpy as np
from matplotlib import dates as mpldates
import matplotlib.pyplot as plt
import requests as r
import bisect as bs
from collections import deque 
import datetime
import Utils

#AGGREGATION_PERIOD_LENGTH = 60 * 1000 
AGGREGATION_PERIOD_LENGTH = 1000 

def rescale_ob(ob_prices, ob_volumes, time_span_length, volume_per_time_unit):
    ps_up_volume = ob_volumes[:]            # prefix sum
    for i in range(len(ob_volumes) - 1):
        ps_up_volume[i + 1] += ps_up_volume[i]
    
    expected_volume = 0.0
    scaled_ob_prices = []
    
    time_step = AGGREGATION_PERIOD_LENGTH 
    for t in range(0, time_span_length, time_step):
        expected_volume += volume_per_time_unit * time_step
        ix = bs.bisect_right(ps_up_volume, expected_volume)
        if ix < len(ob_prices):
            scaled_ob_prices.append(ob_prices[ix])                           #price found by expected volume
        else:
            break
    return scaled_ob_prices

def to_mpl_date(ts):
    d = datetime.datetime.fromtimestamp(ts / 1000) 
    mpd = mpldates.date2num(d)
    return mpd

#P0 x6 volumes
#P1 [45040, 45040, 45020, 45010, 45000, 45000, 45000, 44980, 44980, 44970]
#P2 [44900, 44900, 44900, 44900, 44900, 44900, 44900, 44900, 44900, 44900]
#P3 [44000, 44000, 44000, 44000, 44000, 44000, 44000, 44000, 44000, 44000]
#Level of price aggregation (P0, P1, P2, P3, P4, R0)


plt.show()
plt.style.use('dark_background')        # SEE ALSO: https://stackoverflow.com/questions/23444413/change-a-charts-border-area-color

# TODO: longer time period to plot - 10-20 mins, on web gui - add a control
# TODO: control  for different OB aggregations
# TODO: control to select marker

MAX_TRADE_LEN = 400         # TODO: trade orders vs time - now it's orders
trade_prices = deque(maxlen = MAX_TRADE_LEN)
trade_times = deque(maxlen = MAX_TRADE_LEN)
trade_volumes = deque(maxlen = MAX_TRADE_LEN)

MAX_OB_DECK = 10
ob_deck = deque(maxlen = MAX_OB_DECK)

def load_ob():
    ret = r.get("https://api-pub.bitfinex.com/v2/book/tBTCUSD/P1")
    values = ret.json()
    up = [v[0] for v in values if v[-1] > 0]                    # price levels
    up_volume_list = [v[-1] for v in values if v[-1] > 0]       # volumes
    
    down = [v[0] for v in values if v[-1] < 0]
    down_volume_list = [abs(v[-1]) for v in values if v[-1] < 0]
    return down, down_volume_list, up, up_volume_list

while True:

    plt.clf()
    plt.grid(b = True, c="#006464")

    aggregation_period = AGGREGATION_PERIOD_LENGTH
    ts_now = datetime.datetime.now().timestamp() * 1000 
    limit_time  = (1 + trade_times[-1]) if len(trade_times) else (ts_now - aggregation_period * 10)

    #truncated_prices, truncated_volumes, tuncated_times = Utils.load_aggregated_trades(limit_time, "1m")
    truncated_prices, truncated_volumes, tuncated_times = Utils.load_trades(limit_time)

    trade_times += tuncated_times
    trade_prices += truncated_prices
    trade_volumes += truncated_volumes

    # plot price graph
    plt.plot([to_mpl_date(t) for t in trade_times], trade_prices, 'b')
    ax = plt.axes()
    ax.set_facecolor('black')

    xfmt = mpldates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)

    # plot trades with color coded volumes
    max_volume = max(trade_volumes)
    min_volume = min(trade_volumes)

    volume_color_values = [100 + int(155 / (max_volume - min_volume) * v) for v in trade_volumes]
    volume_colors = ['#%02x0000' % int(v) for v in volume_color_values]

    #plt.scatter(trade_times, trade_prices, c=volume_colors)
    plt.scatter([to_mpl_date(t) for t in trade_times], trade_prices)

    # plot the order book
    down, down_volume_list, up, up_volume_list = load_ob()

    volume = sum(trade_volumes)                                     # SEEMS NOT: if the trades are recorded twice - as SELL and as BUY - in this case the VOLUME is doubled
                                                                    # MAYBE: check if signed_trade_volumes offset over time
    time_span_length = trade_times[-1] - trade_times[0]
    volume_per_time_unit = volume / (trade_times[-1] - trade_times[0])                               # per millisecond

    scaled_up = rescale_ob(up, up_volume_list, time_span_length, volume_per_time_unit)
    scaled_down = rescale_ob(down, down_volume_list, time_span_length, volume_per_time_unit)

    ob_deck.append((trade_times[-1], scaled_up, scaled_down))

    color_step = int(255 / (len(ob_deck)))
    color = 0
    for st, su, sd in ob_deck:
        color += color_step 
        plt.plot([to_mpl_date(st + AGGREGATION_PERIOD_LENGTH * i) for i in range(len(su))], su, '#%02x0000' % color)
        plt.plot([to_mpl_date(st + AGGREGATION_PERIOD_LENGTH * i) for i in range(len(sd))], sd, '#00%02x00' % color)

    #plt.pause(0.005) # for better animation see https://matplotlib.org/3.1.1/api/animation_api.html#module-matplotlib.animation
    plt.pause(1) # should correspond to aggregation

