import requests as r
from collections import namedtuple
CandlePrices = namedtuple("CandlePrices", ["open", "close", "high", "low"])

def load_candles(limit_time, aggregation="1m"):
    '''
    aggregation = 1m, 5m, ...
    '''

    url = "https://api-pub.bitfinex.com/v2/candles/trade:{1}:tBTCUSD/hist?sort=1&start={0}".format(limit_time, aggregation)

    ret = r.get(url)
    values = ret.json()

    #[1614459540000,47076,47080,47091,47052,1.51903903]
    #[ts, open, close, high, low, vol]
    candle_times = [v[0] for v in values]
    candle_prices = [CandlePrices(*v[1:5]) for v in values]
    candle_volumes = [abs(v[5]) for v in values]

    return candle_prices, candle_volumes, candle_times

def candles2trades(candle_prices, candle_volumes, candle_times):
    trade_times = []
    trade_prices = []
    trade_volumes = []

    if len(candle_prices) < 2:
        return [], [], []

    time_span = candle_times[1] - candle_times[0]
    for candle_4price, candle_volume, candle_time in zip(candle_prices, candle_volumes, candle_times):
        trade_times += [candle_time + time_span // 4 * t for t in range(4)]
        trade_prices += [candle_4price.open, candle_4price.low, candle_4price.high, candle_4price.close]
        trade_volumes += [candle_volume / 4] * 4

    return trade_prices, trade_volumes, trade_times

def load_aggregated_trades(limit_time, aggregation):
    return candles2trades(*load_candles(limit_time, aggregation))

def load_trades(limit_time):
    url = "https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist?sort=1&start={}".format(limit_time)

    ret = r.get(url)
    values = ret.json()
    unsorted_trade_prices = [v[-1] for v in values]
    unsorted_trade_times = [v[1] for v in values]
    unsorted_trade_volumes = [abs(v[-2]) for v in values]

    return unsorted_trade_prices, unsorted_trade_volumes, unsorted_trade_times
