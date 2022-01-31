from CryptoBackTest import *

# Paste your own api keys which you can get by creating a Binance account
api_key = 'WDpBVEVMc3wjLCAYQ4opBgpHNhDlT0ClZH25OZml4C0ocygkDR30JggMOr5kKYrK'
api_secret_key = '51iVBjoSMhu4NkU85d7SiVrGpMwOB2eyPTHbvKe1zW1iHWquhXqg3rIwcu29anKK'

# Enter a ticker symbol (ex: ETHUSDT, ETHBTC, SOLUSDT...)
asset = "BTCUSDT"

# Available timeframes : 1min, 3min, 5min, 15min, 30min, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1m
timeFrame = "1d"

# Choose the start date of the backtest (Follow this format: "1 Jan, 2020")
startDate = "1 Jan, 2020"


test1 = CryptoBackTest(api_key, api_secret_key, asset, timeFrame, startDate)
test1.buysell1sma(2, 10)
# test1.buysell1ema()
# test1.buy1ema()
# test1.buy2ema()
# test1.buy3ema()
# test1.plot()
