import requests as r

def load_trades(limit_time):
    if limit_time:
        url = "https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist?sort=1&start={}&".format(limit_time)
    else:
        url = "https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist"

    ret = r.get(url)
    values = ret.json()
    unsorted_trade_prices = [v[-1] for v in values]
    unsorted_trade_times = [v[1] for v in values]
    unsorted_trade_volumes = [abs(v[-2]) for v in values]

    return unsorted_trade_prices, unsorted_trade_volumes, unsorted_trade_times
