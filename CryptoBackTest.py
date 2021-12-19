from binance.client import Client
import csv
import datetime
import pandas as pd
import mplfinance as mpf

api_key = 'WDpBVEVMc3wjLCAYQ4opBgpHNhDlT0ClZH25OZml4C0ocygkDR30JggMOr5kKYrK'
api_secret = '51iVBjoSMhu4NkU85d7SiVrGpMwOB2eyPTHbvKe1zW1iHWquhXqg3rIwcu29anKK'

client = Client(api_key, api_secret)

# prices = client.get_all_tickers()
#
# for price in prices:
#     print(prices)

# return string: Open time,Open,High,Low,Close,Volume,Close time,Quote asset volume,Number of trades,
# Taker buy base asset,Taker buy quote asset volume,Ignore.
# candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_4HOUR)
candles = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_4HOUR, "1 Sep, 2019")
csvfile = open('4hours.csv', 'w', newline='')
candlestick_writer = csv.writer(csvfile, delimiter=',')


for candlestick in candles:
    # print(candlestick)
    candlestick_writer.writerow(candlestick)
# print(len(candles))

# convert csv into dataframe to plot
pd4hours = pd.read_csv('4hours.csv', index_col=False, parse_dates=True, header=None)

# convert epoch time to DateTime
for i in range(len(pd4hours[0])):
    epoch = int(pd4hours.iloc[i][0]) / 1000
    date_time = datetime.datetime.fromtimestamp(epoch)
    # date_time = pd.to_datetime(epoch)
    pd4hours.at[i, 0] = date_time

# give column names
pd4hours.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                    'Number of trades', 'Taker buy base asset', 'Taker buy quote asset volume', 'Ignore']
# print(pd4hours)

# drop useless columns
pd4hours.drop(columns=['Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset',
                       'Taker buy quote asset volume', 'Ignore'], inplace=True)

# put datetime as index
pd4hours.set_index('Date', inplace=True)
# print(pd4hours)

# data analysis
# Performance over time calculation
firstValue = pd4hours.iloc[0][3]
lastValue = pd4hours.iloc[len(pd4hours['Open'])-1][3]
assetPerformance = "%.2f" % (((lastValue-firstValue)/firstValue)*100)


# # BackTest with 1 EMA Only Buying
# bestEMA = 0
# bestPerf = 0
# for j in range(2, 300):
#     # creation and calculation for EMA
#     emaperiod = j
#     multiplier = 2/(emaperiod+1)
#     pd4hours["EMA"] = float("NaN")
#     somme = 0
#     for i in range(0, emaperiod):
#         somme += pd4hours.iloc[i][3]
#     SMA = somme / emaperiod
#     pd4hours.iloc[emaperiod-1, 4] = SMA
#     for i in range(emaperiod, len(pd4hours['Open'])):
#         pd4hours.iloc[i, 4] = (pd4hours.iloc[i, 3] * multiplier) + (pd4hours.iloc[i-1, 4] * (1 - multiplier))
#
#     # ema strategy backTest
#     buying = False
#     buyPrice = 0
#     sellPrice = 0
#     K = 1
#     tradeCount = 0
#     for i in range(len(pd4hours['Open'])):
#         if (pd4hours.iloc[i][4] < pd4hours.iloc[i][3]) and not buying:
#             buyPrice = pd4hours.iloc[i][3]
#             buying = True
#         elif (pd4hours.iloc[i][4] > pd4hours.iloc[i][3]) and buying:
#             sellPrice = pd4hours.iloc[i][3]
#             tradePerf = ((sellPrice-buyPrice)/buyPrice)
#             tradeCount += 1
#             # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
#             K = K*(sellPrice/buyPrice)
#             buying = False
#     stratPerf = (K - 1)*100
#     if stratPerf > bestPerf:
#         bestPerf = stratPerf
#         bestEMA = emaperiod
#     print('EMA '+str(emaperiod)+' Performance: '+str("%.2f" % stratPerf)+' % with '+str(tradeCount)+' trades')
# print('Asset Performance from '+str(pd4hours.index[0]) + ' to '
#       + str(pd4hours.index[-1]) + ' : ' + str(assetPerformance) + ' %')
# print('The best performance is: EMA '+str(bestEMA)+' '+str("%.2f" % bestPerf)+' %')

# # BackTest with 2 EMA Only Buying
# bestEMA1 = 0
# bestEMA2 = 0
# bestPerf = 0

# for k in range(2, 300, 10):
#     for j in range(2, 300, 10):
#         # creation and calculation for EMA
#         ema1period = j
#         ema2period = k
#         multiplier1 = 2/(ema1period+1)
#         multiplier2 = 2/(ema2period+1)
#         pd4hours["EMA1"] = float("NaN")
#         pd4hours["EMA2"] = float("NaN")
#
#         # fill the EMA columns with values
#         somme = 0
#         for i in range(0, ema1period):
#             somme += pd4hours.iloc[i][3]
#         SMA = somme / ema1period
#         pd4hours.iloc[ema1period-1, 4] = SMA
#         for i in range(ema1period, len(pd4hours['Open'])):
#             pd4hours.iloc[i, 4] = (pd4hours.iloc[i, 3] * multiplier1) + (pd4hours.iloc[i-1, 4] * (1 - multiplier1))
#         somme = 0
#         for i in range(0, ema2period):
#             somme += pd4hours.iloc[i][3]
#         SMA = somme / ema2period
#         pd4hours.iloc[ema2period-1, 5] = SMA
#         for i in range(ema2period, len(pd4hours['Open'])):
#             pd4hours.iloc[i, 5] = (pd4hours.iloc[i, 3] * multiplier2) + (pd4hours.iloc[i-1, 4] * (1 - multiplier2))
#
#         # backTest
#         buying = False
#         buyPrice = 0
#         sellPrice = 0
#         K = 1
#         tradeCount = 0
#         for i in range(len(pd4hours['Open'])):
#             if (pd4hours.iloc[i][4] < pd4hours.iloc[i][3]) and \
#                     (pd4hours.iloc[i][5] < pd4hours.iloc[i][3]) and not buying:
#                 buyPrice = pd4hours.iloc[i][3]
#                 buying = True
#             elif ((pd4hours.iloc[i][4] > pd4hours.iloc[i][3]) or
#                   (pd4hours.iloc[i][5] > pd4hours.iloc[i][3])) and buying:
#                 sellPrice = pd4hours.iloc[i][3]
#                 tradePerf = ((sellPrice-buyPrice)/buyPrice)
#                 tradeCount += 1
#                 # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
#                 K = K*(sellPrice/buyPrice)
#                 buying = False
#         stratPerf = (K - 1)*100
#         if stratPerf > bestPerf:
#             bestPerf = stratPerf
#             bestEMA1 = ema1period
#             bestEMA2 = ema2period
#         print('EMA1 '+str(ema1period)+', EMA2 '+str(ema2period)+' Performance: '+
#                                                     str("%.2f" % stratPerf)+' % with '+str(tradeCount)+' trades')
# print('Asset Performance from '+str(pd4hours.index[0]) + ' to '
#       + str(pd4hours.index[-1]) + ' : ' + str(assetPerformance) + ' %')
# print('The best performance is: EMA1 '+str(bestEMA1)+', EMA2 '+str(bestEMA2)+' '+str("%.2f" % bestPerf)+' %')

# # 3 EMA strategy Only Buying
# for l in range(2, 300, 10):
#     for k in range(2, 300, 10):
#         for j in range(2, 300, 10):
#             # creation and calculation for EMA
#             ema1period = j
#             ema2period = k
#             ema3period = l
#             multiplier1 = 2 / (ema1period + 1)
#             multiplier2 = 2 / (ema2period + 1)
#             multiplier3 = 2 / (ema3period + 1)
#             pd4hours["EMA1"] = float("NaN")
#             pd4hours["EMA2"] = float("NaN")
#             pd4hours["EMA3"] = float("NaN")
#
#             # fill the EMA columns with values
#             somme = 0
#             for i in range(0, ema1period):
#                 somme += pd4hours.iloc[i][3]
#             SMA = somme / ema1period
#             pd4hours.iloc[ema1period - 1, 4] = SMA
#             for i in range(ema1period, len(pd4hours['Open'])):
#                 pd4hours.iloc[i, 4] = (pd4hours.iloc[i, 3] * multiplier1) + (
#                             pd4hours.iloc[i - 1, 4] * (1 - multiplier1))
#             somme = 0
#             for i in range(0, ema2period):
#                 somme += pd4hours.iloc[i][3]
#             SMA = somme / ema2period
#             pd4hours.iloc[ema2period - 1, 5] = SMA
#             for i in range(ema2period, len(pd4hours['Open'])):
#                 pd4hours.iloc[i, 5] = (pd4hours.iloc[i, 3] * multiplier2) + (
#                             pd4hours.iloc[i - 1, 4] * (1 - multiplier2))
#             somme = 0
#             for i in range(0, ema3period):
#                 somme += pd4hours.iloc[i][3]
#             SMA = somme / ema3period
#             pd4hours.iloc[ema3period - 1, 6] = SMA
#             for i in range(ema3period, len(pd4hours['Open'])):
#                 pd4hours.iloc[i, 6] = (pd4hours.iloc[i, 3] * multiplier3) + (
#                         pd4hours.iloc[i - 1, 4] * (1 - multiplier3))
#
#             # backTest
#             buying = False
#             buyPrice = 0
#             sellPrice = 0
#             K = 1
#             tradeCount = 0
#             for i in range(len(pd4hours['Open'])):
#                 if (pd4hours.iloc[i][4] < pd4hours.iloc[i][3]) and (pd4hours.iloc[i][5] < pd4hours.iloc[i][3]) and \
#                         (pd4hours.iloc[i][6] < pd4hours.iloc[i][3]) and not buying:
#                     buyPrice = pd4hours.iloc[i][3]
#                     buying = True
#                 elif ((pd4hours.iloc[i][4] > pd4hours.iloc[i][3]) or (pd4hours.iloc[i][5] > pd4hours.iloc[i][3])
#                       or (pd4hours.iloc[i][6] > pd4hours.iloc[i][3])) and buying:
#                     sellPrice = pd4hours.iloc[i][3]
#                     tradePerf = ((sellPrice - buyPrice) / buyPrice)
#                     tradeCount += 1
#                     # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
#                     K = K * (sellPrice / buyPrice)
#                     buying = False
#             stratPerf = (K - 1)*100
#             if stratPerf > bestPerf:
#                 bestPerf = stratPerf
#                 bestEMA1 = ema1period
#                 bestEMA2 = ema2period
#                 bestEMA3 = ema3period
#             print('EMA1 ' + str(ema1period) + ', EMA2 ' + str(ema2period) + ', EMA3 ' + str(ema3period) +
#                   ' Performance: ' + str("%.2f" % stratPerf) + ' % with ' + str(tradeCount) + ' trades')
# print('Asset Performance from ' + str(pd4hours.index[0]) + ' to ' + str(pd4hours.index[-1]) + ' : ' + str(assetPerformance) + ' %')
# print('The best performance is: EMA1 ' + str(bestEMA1) + ', EMA2 ' + str(bestEMA2)
#       + ', EMA3 ' + str(bestEMA2) + ' ' + str("%.2f" % bestPerf) + ' %')


# BackTest with 1 EMA Buy and Sell - The best performance is: EMA 585 1625.15 % [2, 1000]
bestEMA = 0
bestPerf = 0
bestEMADD = 0
bestEMAnt = 0
start = 2
end = 10
for emaperiod in range(start, end):
    # creation and calculation for EMA
    multiplier = 2/(emaperiod+1)
    pd4hours["EMA"] = float("NaN")
    somme = 0
    for i in range(0, emaperiod):
        somme += pd4hours.iloc[i][3]
    SMA = somme / emaperiod
    pd4hours.iloc[emaperiod-1, 4] = SMA
    for i in range(emaperiod, len(pd4hours['Open'])):
        pd4hours.iloc[i, 4] = (pd4hours.iloc[i, 3] * multiplier) + (pd4hours.iloc[i-1, 4] * (1 - multiplier))

    # ema strategy backTest
    buying = False
    selling = False
    maxDrawdown = 0
    top = 0
    buyPrice = 0
    sellPrice = 0
    K = 1
    tradeCount = 0
    for i in range(end, len((pd4hours['Open']))):
        currentPrice = pd4hours.iloc[i][3]
        currentEMA = pd4hours.iloc[i][4]
        if (currentEMA < currentPrice) and not buying:
            buyPrice = currentPrice
            if selling:
                tradePerf = ((buyPrice - sellPrice) / sellPrice)*(-1)
                tradeCount += 1
                # print('Buying trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                K = K * (buyPrice / sellPrice)
                selling = False
            buying = True
        elif (currentEMA > currentPrice) and not selling:
            sellPrice = currentPrice
            if buying:
                tradePerf = ((sellPrice-buyPrice)/buyPrice)
                tradeCount += 1
                # print('Selling trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                K = K*(sellPrice/buyPrice)
                buying = False
            selling = True
        # calculation of the max drawdown
        if K > top:
            top = K
        elif ((K-top)/top)*100 < maxDrawdown:
            maxDrawdown = ((K-top)/top)*100
    stratPerf = (K - 1)*100
    if stratPerf > bestPerf:
        bestPerf = stratPerf
        bestEMA = emaperiod
        bestEMADD = maxDrawdown
        bestEMAnt = tradeCount
    print('EMA '+str(emaperiod)+' Performance: '+str("%.2f" % stratPerf)+' % with ' +
          str(tradeCount)+' trades, Max Drawdown: '+str(maxDrawdown))
print('Asset Performance from '+str(pd4hours.index[0]) + ' to '
      + str(pd4hours.index[-1]) + ' : ' + str(assetPerformance) + ' %')
print('The best performance is: EMA '+str(bestEMA)+' '+str("%.2f" % bestPerf) +
      ' %, Max Drawdown: '+str("%.2f" % bestEMADD)+' %, Number of trades: '+str(bestEMAnt))


# plot candlestick
# print(pd4hours)
# emaPlot = mpf.make_addplot(pd4hours['EMA'])
# mpf.plot(pd4hours, type='candle', style='binance', addplot=emaPlot, datetime_format='%d-%m-%Y')
csvfile.close()

# valuers NaN de l'EMA
# commencer le backtest à la même date pour toutes les EMA
