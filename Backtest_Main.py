from Backtest_SMA_EMA import *


# Enter a ticker symbol (ex: ETHUSDT, ETHBTC, SOLUSDT...)
asset = "BTCUSDT"

# Available timeframes : 1min, 3min, 5min, 15min, 30min, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1m
timeFrame = "1d"

# Choose a start date for the data (Follow this format: "1 Jan, 2020")
startDate = "1 Jan, 2010"

backtest1 = CryptoBackTest(asset, timeFrame, startDate)

# You can display the raw data graph but a graph will be opened anyway after a backtest
# backtest1.plot()

# Choose if you want to use SMA or EMA and enter as parameter the range of SMA/EMA periods you want to compare
# backtest1.buysell1sma(2, 75)
backtest1.buysell1ema(2, 300)
