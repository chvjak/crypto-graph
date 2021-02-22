import requests as r
import bisect as bs

def load_trades(limit_time):
    ret = r.get("https://api-pub.bitfinex.com/v2/trades/tBTCUSD/hist")
    values = ret.json()
    unsorted_trade_prices = [v[-1] for v in values]
    unsorted_trade_times = [v[1] for v in values]
    unsorted_trade_volumes = [abs(v[-2]) for v in values]
    
    sort_keys = [i for i in range(len(unsorted_trade_times))]
    sort_keys.sort(key=lambda i: unsorted_trade_times[i])
    
    # the bug is connected to the fact that trades batches overlap. the bug is WIP
    # take only those on o later as trade_times[-1]
    sorted_trade_times = [unsorted_trade_times[i] for i in sort_keys]
    sorted_trade_prices = [unsorted_trade_prices[i] for i in sort_keys]
    sorted_trade_volumes = [unsorted_trade_volumes [i] for i in sort_keys]
    
    limit_time_ix = bs.bisect_right(sorted_trade_times, limit_time)
    if limit_time_ix < len(sorted_trade_times):
        tuncated_times = sorted_trade_times[limit_time_ix:]      # TODO: DRY
        truncated_prices = sorted_trade_prices[limit_time_ix:]
        truncated_volumes = sorted_trade_volumes[limit_time_ix:]
    else:
        # nothing to add - same trades
        tuncated_times = []
        truncated_prices = []
        truncated_volumes = []
    return truncated_prices, truncated_volumes, tuncated_times

