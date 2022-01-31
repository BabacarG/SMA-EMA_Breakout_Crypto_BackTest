from binance.client import Client
import csv
import datetime
import pandas as pd
import mplfinance as mpf


class CryptoBackTest:
    def __init__(self, api_key, api_secret, asset, timeFrame, startDate):
        print("Collecting Data...")
        client = Client(api_key, api_secret)
        # prices = client.get_all_tickers()
        #
        # for price in prices:
        #     print(prices)

        # return string: Open time,Open,High,Low,Close,Volume,Close time,Quote asset volume,Number of trades,
        # Taker buy base asset,Taker buy quote asset volume,Ignore.
        # candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_4HOUR)
        # KLINE_INTERVAL_12HOUR,KLINE_INTERVAL_15MINUTE,KLINE_INTERVAL_1DAY,KLINE_INTERVAL_1HOUR,KLINE_INTERVAL_1MINUTE
        # KLINE_INTERVAL_1MONTH,KLINE_INTERVAL_1WEEK, KLINE_INTERVAL_2HOUR, KLINE_INTERVAL_30MINUTE, KLINE_INTERVAL_3DAY
        # KLINE_INTERVAL_3MINUTE,KLINE_INTERVAL_4HOUR,KLINE_INTERVAL_5MINUTE, KLINE_INTERVAL_6HOUR, KLINE_INTERVAL_8HOUR
        binanceTimeFrame = ""
        if timeFrame == "4h":
            binanceTimeFrame = Client.KLINE_INTERVAL_4HOUR
        elif timeFrame == "1d":
            binanceTimeFrame = Client.KLINE_INTERVAL_1DAY
        elif timeFrame == "1min":
            binanceTimeFrame = Client.KLINE_INTERVAL_1MINUTE
        elif timeFrame == "15min":
            binanceTimeFrame = Client.KLINE_INTERVAL_15MINUTE
        elif timeFrame == "3min":
            binanceTimeFrame = Client.KLINE_INTERVAL_3MINUTE
        elif timeFrame == "30min":
            binanceTimeFrame = Client.KLINE_INTERVAL_30MINUTE
        elif timeFrame == "3d":
            binanceTimeFrame = Client.KLINE_INTERVAL_3DAY
        elif timeFrame == "1h":
            binanceTimeFrame = Client.KLINE_INTERVAL_1HOUR
        elif timeFrame == "3d":
            binanceTimeFrame = Client.KLINE_INTERVAL_3DAY

        candles = client.get_historical_klines(asset, binanceTimeFrame, startDate)
        csvfile = open('OHLC.csv', 'w', newline='')
        candlestick_writer = csv.writer(csvfile, delimiter=',')

        for candlestick in candles:
            # print(candlestick)
            candlestick_writer.writerow(candlestick)
        # print(len(candles))

        # convert csv into dataframe to plot
        self.pdOHLC = pd.read_csv('OHLC.csv', index_col=False, parse_dates=True, header=None)

        # convert epoch time to DateTime
        for i in range(len(self.pdOHLC[0])):
            epoch = int(self.pdOHLC.iloc[i][0]) / 1000
            date_time = datetime.datetime.fromtimestamp(epoch)
            # date_time = pd.to_datetime(epoch)
            self.pdOHLC.at[i, 0] = date_time

        # give column names
        self.pdOHLC.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                               'Number of trades', 'Taker buy base asset', 'Taker buy quote asset volume', 'Ignore']
        # print(pd4hours)

        # drop useless columns
        self.pdOHLC.drop(columns=['Volume', 'Close time', 'Quote asset volume', 'Number of trades',
                                  'Taker buy base asset', 'Taker buy quote asset volume', 'Ignore'], inplace=True)

        # put datetime as index
        self.pdOHLC.set_index('Date', inplace=True)
        # print(pd4hours)
        csvfile.close()
        print("Data collected")

    # 2-7200 (1h)

    # 2 - 1800 (4h)
    # Asset Performance from 2018-06-14 14:00:00 to 2022-01-14 21:00:00 : 578.71 %s
    # The best performance is SMA 261: 2502.18 %
    # Number of trades: 140
    # Max Drawdown: -32.51 %
    # Winning trades average: 36.81 %
    # Losing trades average: -1.43 %
    # Buying trades average: 6.87 %
    # Selling trades average: 0.64 %

    # 2 - 300 (1d)
    # Asset Performance from 2018-06-13 02:00:00 to 2021-12-09 01:00:00 : 655.56 %
    # The best performance is SMA 124: 1591.12 %
    # Number of trades: 14
    # Max Drawdown: -30.76 %
    # Winning trades average: 100.54 %
    # Losing trades average: -7.76 %
    # Buying trades average: 87.58 %
    # Selling trades average: 5.20 %

    # 2 - 100 (3d)

    def buysell1sma(self, start, end):
        print('Processing the backtest from ' + str(self.pdOHLC.index[end]))
        # print(self.pd4hours)

        # BackTest with 1 SMA Buy and Sell
        bestPerf = -99999999
        bestSMA = 0
        bestSMADD = 0
        bestSMAnt = 0
        saferDD = - 101
        saferSMA = 0
        saferPerf = 0
        saferSMAnt = 0
        bestSTA = 0
        bestBTA = 0
        bestWTA = 0
        bestLTA = 0
        saferSTA = 0
        saferBTA = 0
        saferWTA = 0
        saferLTA = 0
        bestChart = self.pdOHLC.copy(deep=True)
        for smaperiod in range(start, end + 1):
            # creation and calculation for SMA
            self.pdOHLC["SMA"] = self.pdOHLC["Close"].rolling(smaperiod).mean()
            self.pdOHLC["Equity"] = float("NaN")
            # sma strategy backTest
            buying = False
            selling = False
            maxDrawdown = 0
            top = 0
            buyPrice = 0
            sellPrice = 0
            K = self.pdOHLC.iloc[end][3]
            tradeCount = 0

            sellingTradesSum = 0
            buyingTradesSum = 0
            winningTradesSum = 0
            losingTradesSum = 0
            sellingTradesCount = 0
            buyingTradesCount = 0
            winningTradesCount = 0
            losingTradesCount = 0

            for i in range(end, len((self.pdOHLC['Open']))):
                currentPrice = self.pdOHLC.iloc[i][3]
                currentSMA = self.pdOHLC.iloc[i][4]
                if (currentSMA < currentPrice) and (not buying):
                    buyPrice = currentPrice
                    if selling:
                        tradePerf = ((sellPrice - buyPrice) / sellPrice)
                        sellingTradesSum += tradePerf
                        sellingTradesCount += 1
                        if tradePerf > 0:
                            winningTradesSum += tradePerf
                            winningTradesCount += 1
                        else:
                            losingTradesSum += tradePerf
                            losingTradesCount += 1
                        tradeCount += 1
                        # print('Buying trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                        K = K * (2 - (buyPrice / sellPrice))
                        selling = False
                    buying = True
                elif (currentSMA > currentPrice) and (not selling):
                    sellPrice = currentPrice
                    if buying:
                        tradePerf = ((sellPrice - buyPrice) / buyPrice)
                        buyingTradesSum += tradePerf
                        buyingTradesCount += 1
                        if tradePerf > 0:
                            winningTradesSum += tradePerf
                            winningTradesCount += 1
                        else:
                            losingTradesSum += tradePerf
                            losingTradesCount += 1
                        tradeCount += 1
                        # print('Selling trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                        K = K * (sellPrice / buyPrice)
                        buying = False
                    selling = True
                self.pdOHLC.iloc[i, 5] = K
                # calculation of the max drawdown
                if K > top:
                    top = K
                elif ((K - top) / top) * 100 < maxDrawdown:
                    maxDrawdown = ((K - top) / top) * 100
            if sellingTradesCount == 0:
                sellingTradesAvg = 0
            else:
                sellingTradesAvg = sellingTradesSum / sellingTradesCount
            if buyingTradesCount == 0:
                buyingTradesAvg = 0
            else:
                buyingTradesAvg = buyingTradesSum / buyingTradesCount
            if winningTradesCount == 0:
                winningTradesAvg = 0
            else:
                winningTradesAvg = winningTradesSum / winningTradesCount
            if losingTradesCount == 0:
                losingTradesAvg = 0
            else:
                losingTradesAvg = losingTradesSum / losingTradesCount

            stratPerf = ((K - self.pdOHLC.iloc[end][3]) / self.pdOHLC.iloc[end][3]) * 100
            if stratPerf > bestPerf:
                bestPerf = stratPerf
                bestSMA = smaperiod
                bestSMADD = maxDrawdown
                bestSMAnt = tradeCount
                bestSTA = sellingTradesAvg
                bestBTA = buyingTradesAvg
                bestWTA = winningTradesAvg
                bestLTA = losingTradesAvg
                bestChart = self.pdOHLC.copy(deep=True)
            if maxDrawdown > saferDD:
                saferDD = maxDrawdown
                saferSMA = smaperiod
                saferSMAnt = tradeCount
                saferPerf = stratPerf
                saferSTA = sellingTradesAvg
                saferBTA = buyingTradesAvg
                saferWTA = winningTradesAvg
                saferLTA = losingTradesAvg

            print('SMA ' + str(smaperiod) + ' Performance: ' + str(stratPerf) + ' % with ' +
                  str(tradeCount) + ' trades, Max Drawdown: ' + str(maxDrawdown))
        firstValue = self.pdOHLC.iloc[end][3]
        lastValue = self.pdOHLC.iloc[len(self.pdOHLC['Open']) - 1][3]
        assetPerformance = "%.2f" % (((lastValue - firstValue) / firstValue) * 100)

        print(" ")
        print('Asset Performance from ' + str(self.pdOHLC.index[end]) + ' to '
              + str(self.pdOHLC.index[-1]) + ' : ' + str(assetPerformance) + ' %')
        print(" ")

        print('The best performance is SMA ' + str(bestSMA) + ': ' + str("%.2f" % bestPerf) + ' %')
        print('Number of trades: ' + str(bestSMAnt))
        print('Max Drawdown: ' + str("%.2f" % bestSMADD) + ' %')
        print('Winning trades average: ' + str("%.2f" % (bestWTA * 100)) + ' %')
        print('Losing trades average: ' + str("%.2f" % (bestLTA * 100)) + ' %')
        print('Buying trades average: ' + str("%.2f" % (bestBTA * 100)) + ' %')
        print('Selling trades average: ' + str("%.2f" % (bestSTA * 100)) + ' %')
        print(" ")

        print('The safer strategy is SMA ' + str(saferSMA) + ': ' + str("%.2f" % saferPerf) + ' %')
        print('Number of trades: ' + str(saferSMAnt))
        print('Max Drawdown: ' + str("%.2f" % saferDD) + ' %')
        print('Winning trades average: ' + str("%.2f" % (saferWTA * 100)) + ' %')
        print('Losing trades average: ' + str("%.2f" % (saferLTA * 100)) + ' %')
        print('Buying trades average: ' + str("%.2f" % (saferBTA * 100)) + ' %')
        print('Selling trades average: ' + str("%.2f" % (saferSTA * 100)) + ' %')

        self.pdOHLC = bestChart
        self.plot(False, True, True)

    # 2 - 3000 :
    # Asset Performance from 2017-08-17 06:00:00 to 2021-12-29 05:00:00 : 1272.68 %
    # The best performance is: EMA 216 1540.02 %, Max Drawdown: -41.35 %, Number of trades: 160
    # The safer strategy is: EMA 1779 1154.38 %, Max Drawdown: -4.10 %, Number of trades: 73
    def buysell1ema(self):
        print('ok')

        # BackTest with 1 EMA Buy and Sell - The best performance is: EMA 585 1625.15 % [2, 1000]
        bestPerf = 0.0
        bestEMA = 0
        bestEMADD = 0
        bestEMAnt = 0
        saferDD = - 101
        saferEMA = 0
        saferPerf = 0
        saferEMAnt = 0
        start = 2
        end = 5
        for emaperiod in range(start, end + 1):
            # creation and calculation for EMA
            multiplier = 2 / (emaperiod + 1)
            self.pdOHLC["EMA"] = float("NaN")
            for i in range(len(self.pdOHLC['Open'])):
                self.pdOHLC.iloc[i - 1, 4] = float("NaN")
            somme = 0
            for i in range(0, emaperiod):
                somme += self.pdOHLC.iloc[i][3]
            SMA = somme / emaperiod
            self.pdOHLC.iloc[emaperiod - 1, 4] = SMA
            for i in range(emaperiod, len(self.pdOHLC['Open'])):
                self.pdOHLC.iloc[i, 4] = (self.pdOHLC.iloc[i, 3] * multiplier) + \
                                         (self.pdOHLC.iloc[i - 1, 4] * (1 - multiplier))

            # ema strategy backTest
            buying = False
            selling = False
            maxDrawdown = 0
            top = 0
            buyPrice = 0
            sellPrice = 0
            K = 1.0
            tradeCount = 0
            for i in range(end, len((self.pdOHLC['Open']))):
                currentPrice = self.pdOHLC.iloc[i][3]
                currentEMA = self.pdOHLC.iloc[i][4]
                if (currentEMA < currentPrice) and (not buying):
                    buyPrice = currentPrice
                    if selling:
                        # tradePerf = ((buyPrice - sellPrice) / sellPrice) * (-1)
                        tradeCount += 1
                        # print('Buying trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                        K = K * (buyPrice / sellPrice)
                        selling = False
                    buying = True
                elif (currentEMA > currentPrice) and (not selling):
                    sellPrice = currentPrice
                    if buying:
                        # tradePerf = ((sellPrice - buyPrice) / buyPrice)
                        tradeCount += 1
                        # print('Selling trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                        K = K * (sellPrice / buyPrice)
                        buying = False
                    selling = True
                # calculation of the max drawdown
                if K > top:
                    top = K
                elif ((K - top) / top) * 100 < maxDrawdown:
                    maxDrawdown = ((K - top) / top) * 100
            stratPerf = (K - 1) * 100
            if stratPerf > bestPerf:
                bestPerf = stratPerf
                bestEMA = emaperiod
                bestEMADD = maxDrawdown
                bestEMAnt = tradeCount
            if maxDrawdown > saferDD:
                saferDD = maxDrawdown
                saferEMA = emaperiod
                saferEMAnt = tradeCount
                saferPerf = stratPerf

            print('EMA ' + str(emaperiod) + ' Performance: ' + str(stratPerf) + ' % with ' +
                  str(tradeCount) + ' trades, Max Drawdown: ' + str(maxDrawdown))
        print('Asset Performance from ' + str(self.pdOHLC.index[0]) + ' to '
              + str(self.pdOHLC.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA ' + str(bestEMA) + ' ' + str("%.2f" % bestPerf) +
              ' %, Max Drawdown: ' + str("%.2f" % bestEMADD) + ' %, Number of trades: ' + str(bestEMAnt))
        print('The safer strategy is: EMA ' + str(saferEMA) + ' ' + str("%.2f" % saferPerf) +
              ' %, Max Drawdown: ' + str("%.2f" % saferDD) + ' %, Number of trades: ' + str(saferEMAnt))
        # self.plot()

    # plot candlestick
    def plot(self, ema, sma, equity):
        if ema and equity:
            otherPlots = [mpf.make_addplot(self.pdOHLC['EMA'], color='g'), mpf.make_addplot(self.pdOHLC['Equity'])]
        elif sma and equity:
            otherPlots = [mpf.make_addplot(self.pdOHLC['SMA'], color='g', secondary_y=False),
                          mpf.make_addplot(self.pdOHLC['Equity'], secondary_y=False)]
        elif ema:
            otherPlots = mpf.make_addplot(self.pdOHLC['EMA'], color='g', secondary_y=False)
        elif sma:
            otherPlots = mpf.make_addplot(self.pdOHLC['SMA'], color='g', secondary_y=False)
        elif equity:
            otherPlots = mpf.make_addplot(self.pdOHLC['Equity'], secondary_y=False)
        else:
            data = pd.DataFrame()
            otherPlots = mpf.make_addplot(data)
        mpf.plot(self.pdOHLC, type='candle', style='binance', datetime_format='%d-%m-%Y', warn_too_much_data=99000,
                 addplot=otherPlots, scale_width_adjustment=dict(lines=0.85))

    # BackTest with 1 EMA Only Buying
    def buy1ema(self):
        bestEMA = 0
        bestPerf = 0
        for j in range(2, 300):
            # creation and calculation for EMA
            emaperiod = j
            multiplier = 2 / (emaperiod + 1)
            self.pdOHLC["EMA"] = float("NaN")
            somme = 0
            for i in range(0, emaperiod):
                somme += self.pdOHLC.iloc[i][3]
            SMA = somme / emaperiod
            self.pdOHLC.iloc[emaperiod - 1, 4] = SMA
            for i in range(emaperiod, len(self.pdOHLC['Open'])):
                self.pdOHLC.iloc[i, 4] = (self.pdOHLC.iloc[i, 3] * multiplier) + \
                                         (self.pdOHLC.iloc[i - 1, 4] * (1 - multiplier))

            # ema strategy backTest
            buying = False
            buyPrice = 0
            K = 1
            tradeCount = 0
            for i in range(len(self.pdOHLC['Open'])):
                if (self.pdOHLC.iloc[i][4] < self.pdOHLC.iloc[i][3]) and not buying:
                    buyPrice = self.pdOHLC.iloc[i][3]
                    buying = True
                elif (self.pdOHLC.iloc[i][4] > self.pdOHLC.iloc[i][3]) and buying:
                    sellPrice = self.pdOHLC.iloc[i][3]
                    # tradePerf = ((sellPrice - buyPrice) / buyPrice)
                    tradeCount += 1
                    # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                    K = K * (sellPrice / buyPrice)
                    buying = False
            stratPerf = (K - 1) * 100
            if stratPerf > bestPerf:
                bestPerf = stratPerf
                bestEMA = emaperiod
            print('EMA ' + str(emaperiod) + ' Performance: ' + str("%.2f" % stratPerf) + ' % with ' + str(
                tradeCount) + ' trades')
        print('Asset Performance from ' + str(self.pdOHLC.index[0]) + ' to '
              + str(self.pdOHLC.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA ' + str(bestEMA) + ' ' + str("%.2f" % bestPerf) + ' %')

    # BackTest with 2 EMA Only Buying
    def buy2ema(self):
        print('ok')
        bestEMA1 = 0
        bestEMA2 = 0
        bestPerf = 0

        for k in range(2, 300, 10):
            for j in range(2, 300, 10):
                # creation and calculation for EMA
                ema1period = j
                ema2period = k
                multiplier1 = 2 / (ema1period + 1)
                multiplier2 = 2 / (ema2period + 1)
                self.pdOHLC["EMA1"] = float("NaN")
                self.pdOHLC["EMA2"] = float("NaN")

                # fill the EMA columns with values
                somme = 0
                for i in range(0, ema1period):
                    somme += self.pdOHLC.iloc[i][3]
                SMA = somme / ema1period
                self.pdOHLC.iloc[ema1period - 1, 4] = SMA
                for i in range(ema1period, len(self.pdOHLC['Open'])):
                    self.pdOHLC.iloc[i, 4] = (self.pdOHLC.iloc[i, 3] * multiplier1) + \
                                             (self.pdOHLC.iloc[i - 1, 4] * (1 - multiplier1))
                somme = 0
                for i in range(0, ema2period):
                    somme += self.pdOHLC.iloc[i][3]
                SMA = somme / ema2period
                self.pdOHLC.iloc[ema2period - 1, 5] = SMA
                for i in range(ema2period, len(self.pdOHLC['Open'])):
                    self.pdOHLC.iloc[i, 5] = (self.pdOHLC.iloc[i, 3] * multiplier2) + \
                                             (self.pdOHLC.iloc[i - 1, 4] * (1 - multiplier2))

                # backTest
                buying = False
                buyPrice = 0
                K = 1
                tradeCount = 0
                for i in range(len(self.pdOHLC['Open'])):
                    if (self.pdOHLC.iloc[i][4] < self.pdOHLC.iloc[i][3]) and \
                            (self.pdOHLC.iloc[i][5] < self.pdOHLC.iloc[i][3]) and not buying:
                        buyPrice = self.pdOHLC.iloc[i][3]
                        buying = True
                    elif ((self.pdOHLC.iloc[i][4] > self.pdOHLC.iloc[i][3]) or
                          (self.pdOHLC.iloc[i][5] > self.pdOHLC.iloc[i][3])) and buying:
                        sellPrice = self.pdOHLC.iloc[i][3]
                        # tradePerf = ((sellPrice - buyPrice) / buyPrice)
                        tradeCount += 1
                        # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                        K = K * (sellPrice / buyPrice)
                        buying = False
                stratPerf = (K - 1) * 100
                if stratPerf > bestPerf:
                    bestPerf = stratPerf
                    bestEMA1 = ema1period
                    bestEMA2 = ema2period
                print('EMA ' + str(ema1period) + ', EMA ' + str(ema2period) + ' Performance: '
                      + str("%.2f" % stratPerf) + ' % with ' + str(tradeCount) + ' trades')
        print('Asset Performance from ' + str(self.pdOHLC.index[0]) + ' to '
              + str(self.pdOHLC.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA1 ' + str(bestEMA1) + ', EMA2 ' + str(bestEMA2) + ' ' + str(
            "%.2f" % bestPerf) + ' %')

    # 3 EMA strategy Only Buying
    def buy3ema(self):
        bestPerf = 0
        bestEMA1 = 0
        bestEMA2 = 0
        bestEMA3 = 0
        for l in range(2, 300, 10):
            for k in range(2, 300, 10):
                for j in range(2, 300, 10):
                    # creation and calculation for EMA
                    ema1period = j
                    ema2period = k
                    ema3period = l
                    multiplier1 = 2 / (ema1period + 1)
                    multiplier2 = 2 / (ema2period + 1)
                    multiplier3 = 2 / (ema3period + 1)
                    self.pdOHLC["EMA1"] = float("NaN")
                    self.pdOHLC["EMA2"] = float("NaN")
                    self.pdOHLC["EMA3"] = float("NaN")

                    # fill the EMA columns with values
                    somme = 0
                    for i in range(0, ema1period):
                        somme += self.pdOHLC.iloc[i][3]
                    SMA = somme / ema1period
                    self.pdOHLC.iloc[ema1period - 1, 4] = SMA
                    for i in range(ema1period, len(self.pdOHLC['Open'])):
                        self.pdOHLC.iloc[i, 4] = (self.pdOHLC.iloc[i, 3] * multiplier1) + (
                                self.pdOHLC.iloc[i - 1, 4] * (1 - multiplier1))
                    somme = 0
                    for i in range(0, ema2period):
                        somme += self.pdOHLC.iloc[i][3]
                    SMA = somme / ema2period
                    self.pdOHLC.iloc[ema2period - 1, 5] = SMA
                    for i in range(ema2period, len(self.pdOHLC['Open'])):
                        self.pdOHLC.iloc[i, 5] = (self.pdOHLC.iloc[i, 3] * multiplier2) + (
                                self.pdOHLC.iloc[i - 1, 4] * (1 - multiplier2))
                    somme = 0
                    for i in range(0, ema3period):
                        somme += self.pdOHLC.iloc[i][3]
                    SMA = somme / ema3period
                    self.pdOHLC.iloc[ema3period - 1, 6] = SMA
                    for i in range(ema3period, len(self.pdOHLC['Open'])):
                        self.pdOHLC.iloc[i, 6] = (self.pdOHLC.iloc[i, 3] * multiplier3) + (
                                self.pdOHLC.iloc[i - 1, 4] * (1 - multiplier3))

                    # backTest
                    buying = False
                    buyPrice = 0
                    K = 1
                    tradeCount = 0
                    for i in range(len(self.pdOHLC['Open'])):
                        if (self.pdOHLC.iloc[i][4] < self.pdOHLC.iloc[i][3]) and \
                                (self.pdOHLC.iloc[i][5] < self.pdOHLC.iloc[i][3]) and \
                                (self.pdOHLC.iloc[i][6] < self.pdOHLC.iloc[i][3]) and not buying:
                            buyPrice = self.pdOHLC.iloc[i][3]
                            buying = True
                        elif ((self.pdOHLC.iloc[i][4] > self.pdOHLC.iloc[i][3]) or
                              (self.pdOHLC.iloc[i][5] > self.pdOHLC.iloc[i][3])
                              or (self.pdOHLC.iloc[i][6] > self.pdOHLC.iloc[i][3])) and buying:
                            sellPrice = self.pdOHLC.iloc[i][3]
                            # tradePerf = ((sellPrice - buyPrice) / buyPrice)
                            tradeCount += 1
                            # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                            K = K * (sellPrice / buyPrice)
                            buying = False
                    stratPerf = (K - 1) * 100
                    if stratPerf > bestPerf:
                        bestPerf = stratPerf
                        bestEMA1 = ema1period
                        bestEMA2 = ema2period
                        bestEMA3 = ema3period
                    print('EMA ' + str(ema1period) + ', EMA ' + str(ema2period) + ', EMA ' + str(ema3period) +
                          ' Performance: ' + str("%.2f" % stratPerf) + ' % with ' + str(tradeCount) + ' trades')
        print('Asset Performance from ' + str(self.pdOHLC.index[0]) + ' to ' +
              str(self.pdOHLC.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA ' + str(bestEMA1) + ', EMA ' + str(bestEMA2)
              + ', EMA3 ' + str(bestEMA3) + ' ' + str("%.2f" % bestPerf) + ' %')
