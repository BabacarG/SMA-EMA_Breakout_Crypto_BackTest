from binance.client import Client
import csv
import datetime
import pandas as pd
import mplfinance as mpf


class CryptoBackTest:
    def __init__(self, api_key, api_secret, asset, timeFrame, startDate):

        client = Client(api_key, api_secret)
        # prices = client.get_all_tickers()
        #
        # for price in prices:
        #     print(prices)

        # return string: Open time,Open,High,Low,Close,Volume,Close time,Quote asset volume,Number of trades,
        # Taker buy base asset,Taker buy quote asset volume,Ignore.
        # candles = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_4HOUR)
        binanceTimeFrame = ""
        if timeFrame == "4hours":
            binanceTimeFrame = Client.KLINE_INTERVAL_4HOUR
        candles = client.get_historical_klines(asset, binanceTimeFrame, startDate)
        csvfile = open('4hours.csv', 'w', newline='')
        candlestick_writer = csv.writer(csvfile, delimiter=',')

        for candlestick in candles:
            # print(candlestick)
            candlestick_writer.writerow(candlestick)
        # print(len(candles))

        # convert csv into dataframe to plot
        self.pd4hours = pd.read_csv('4hours.csv', index_col=False, parse_dates=True, header=None)

        # convert epoch time to DateTime
        for i in range(len(self.pd4hours[0])):
            epoch = int(self.pd4hours.iloc[i][0]) / 1000
            date_time = datetime.datetime.fromtimestamp(epoch)
            # date_time = pd.to_datetime(epoch)
            self.pd4hours.at[i, 0] = date_time

        # give column names
        self.pd4hours.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                                 'Number of trades', 'Taker buy base asset', 'Taker buy quote asset volume', 'Ignore']
        # print(pd4hours)

        # drop useless columns
        self.pd4hours.drop(columns=['Volume', 'Close time', 'Quote asset volume', 'Number of trades',
                                    'Taker buy base asset', 'Taker buy quote asset volume', 'Ignore'], inplace=True)

        # put datetime as index
        self.pd4hours.set_index('Date', inplace=True)
        # print(pd4hours)

        # data analysis
        # Performance over time calculation
        firstValue = self.pd4hours.iloc[0][3]
        lastValue = self.pd4hours.iloc[len(self.pd4hours['Open']) - 1][3]
        self.assetPerformance = "%.2f" % (((lastValue - firstValue) / firstValue) * 100)
        csvfile.close()

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
        start = 5
        end = 10
        for emaperiod in range(start, end+1):
            # creation and calculation for EMA
            multiplier = 2/(emaperiod+1)
            self.pd4hours["EMA"] = float("NaN")
            for i in range(len(self.pd4hours['Open'])):
                self.pd4hours.iloc[i-1, 4] = float("NaN")
            somme = 0
            for i in range(0, emaperiod):
                somme += self.pd4hours.iloc[i][3]
            SMA = somme / emaperiod
            self.pd4hours.iloc[emaperiod-1, 4] = SMA
            for i in range(emaperiod, len(self.pd4hours['Open'])):
                self.pd4hours.iloc[i, 4] = (self.pd4hours.iloc[i, 3] * multiplier) + \
                                           (self.pd4hours.iloc[i-1, 4] * (1 - multiplier))

            # ema strategy backTest
            buying = False
            selling = False
            maxDrawdown = 0
            top = 0
            buyPrice = 0
            sellPrice = 0
            K = 1.0
            tradeCount = 0
            for i in range(end, len((self.pd4hours['Open']))):
                currentPrice = self.pd4hours.iloc[i][3]
                currentEMA = self.pd4hours.iloc[i][4]
                if (currentEMA < currentPrice) and (not buying):
                    buyPrice = currentPrice
                    if selling:
                        tradePerf = ((buyPrice - sellPrice) / sellPrice)*(-1)
                        tradeCount += 1
                        # print('Buying trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                        K = K * (buyPrice / sellPrice)
                        selling = False
                    buying = True
                elif (currentEMA > currentPrice) and (not selling):
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
            if maxDrawdown > saferDD:
                saferDD = maxDrawdown
                saferEMA = emaperiod
                saferEMAnt = tradeCount
                saferPerf = stratPerf

            print('EMA '+str(emaperiod)+' Performance: '+str(stratPerf)+' % with ' +
                  str(tradeCount)+' trades, Max Drawdown: '+str(maxDrawdown))
        print('Asset Performance from '+str(self.pd4hours.index[0]) + ' to '
              + str(self.pd4hours.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA '+str(bestEMA)+' '+str("%.2f" % bestPerf) +
              ' %, Max Drawdown: '+str("%.2f" % bestEMADD)+' %, Number of trades: '+str(bestEMAnt))
        print('The safer strategy is: EMA '+str(saferEMA)+' '+str("%.2f" % saferPerf) +
              ' %, Max Drawdown: '+str("%.2f" % saferDD)+' %, Number of trades: '+str(saferEMAnt))

    # plot candlestick
    def plot(self):
        # emaPlot = mpf.make_addplot(self.pd4hours['EMA'])
        # mpf.plot(self.pd4hours, type='candle', style='binance', addplot=emaPlot, datetime_format='%d-%m-%Y')
        mpf.plot(self.pd4hours, type='candle', style='binance', datetime_format='%d-%m-%Y', warn_too_much_data=9000)

    # BackTest with 1 EMA Only Buying
    def buy1ema(self):
        print('ok')
        bestEMA = 0
        bestPerf = 0
        for j in range(2, 300):
            # creation and calculation for EMA
            emaperiod = j
            multiplier = 2/(emaperiod+1)
            self.pd4hours["EMA"] = float("NaN")
            somme = 0
            for i in range(0, emaperiod):
                somme += self.pd4hours.iloc[i][3]
            SMA = somme / emaperiod
            self.pd4hours.iloc[emaperiod-1, 4] = SMA
            for i in range(emaperiod, len(self.pd4hours['Open'])):
                self.pd4hours.iloc[i, 4] = (self.pd4hours.iloc[i, 3] * multiplier) + \
                                           (self.pd4hours.iloc[i-1, 4] * (1 - multiplier))

            # ema strategy backTest
            buying = False
            buyPrice = 0
            K = 1
            tradeCount = 0
            for i in range(len(self.pd4hours['Open'])):
                if (self.pd4hours.iloc[i][4] < self.pd4hours.iloc[i][3]) and not buying:
                    buyPrice = self.pd4hours.iloc[i][3]
                    buying = True
                elif (self.pd4hours.iloc[i][4] > self.pd4hours.iloc[i][3]) and buying:
                    sellPrice = self.pd4hours.iloc[i][3]
                    tradePerf = ((sellPrice-buyPrice)/buyPrice)
                    tradeCount += 1
                    # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                    K = K*(sellPrice/buyPrice)
                    buying = False
            stratPerf = (K - 1)*100
            if stratPerf > bestPerf:
                bestPerf = stratPerf
                bestEMA = emaperiod
            print('EMA '+str(emaperiod)+' Performance: '+str("%.2f" % stratPerf)+' % with '+str(tradeCount)+' trades')
        print('Asset Performance from '+str(self.pd4hours.index[0]) + ' to '
              + str(self.pd4hours.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA '+str(bestEMA)+' '+str("%.2f" % bestPerf)+' %')

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
                multiplier1 = 2/(ema1period+1)
                multiplier2 = 2/(ema2period+1)
                self.pd4hours["EMA1"] = float("NaN")
                self.pd4hours["EMA2"] = float("NaN")

                # fill the EMA columns with values
                somme = 0
                for i in range(0, ema1period):
                    somme += self.pd4hours.iloc[i][3]
                SMA = somme / ema1period
                self.pd4hours.iloc[ema1period-1, 4] = SMA
                for i in range(ema1period, len(self.pd4hours['Open'])):
                    self.pd4hours.iloc[i, 4] = (self.pd4hours.iloc[i, 3] * multiplier1) + \
                                               (self.pd4hours.iloc[i-1, 4] * (1 - multiplier1))
                somme = 0
                for i in range(0, ema2period):
                    somme += self.pd4hours.iloc[i][3]
                SMA = somme / ema2period
                self.pd4hours.iloc[ema2period-1, 5] = SMA
                for i in range(ema2period, len(self.pd4hours['Open'])):
                    self.pd4hours.iloc[i, 5] = (self.pd4hours.iloc[i, 3] * multiplier2) + \
                                               (self.pd4hours.iloc[i-1, 4] * (1 - multiplier2))

                # backTest
                buying = False
                buyPrice = 0
                K = 1
                tradeCount = 0
                for i in range(len(self.pd4hours['Open'])):
                    if (self.pd4hours.iloc[i][4] < self.pd4hours.iloc[i][3]) and \
                            (self.pd4hours.iloc[i][5] < self.pd4hours.iloc[i][3]) and not buying:
                        buyPrice = self.pd4hours.iloc[i][3]
                        buying = True
                    elif ((self.pd4hours.iloc[i][4] > self.pd4hours.iloc[i][3]) or
                          (self.pd4hours.iloc[i][5] > self.pd4hours.iloc[i][3])) and buying:
                        sellPrice = self.pd4hours.iloc[i][3]
                        tradePerf = ((sellPrice-buyPrice)/buyPrice)
                        tradeCount += 1
                        # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                        K = K*(sellPrice/buyPrice)
                        buying = False
                stratPerf = (K - 1)*100
                if stratPerf > bestPerf:
                    bestPerf = stratPerf
                    bestEMA1 = ema1period
                    bestEMA2 = ema2period
                print('EMA '+str(ema1period)+', EMA '+str(ema2period)+' Performance: '
                      + str("%.2f" % stratPerf)+' % with '+str(tradeCount)+' trades')
        print('Asset Performance from '+str(self.pd4hours.index[0]) + ' to '
              + str(self.pd4hours.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA1 '+str(bestEMA1)+', EMA2 '+str(bestEMA2)+' '+str("%.2f" % bestPerf)+' %')

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
                    self.pd4hours["EMA1"] = float("NaN")
                    self.pd4hours["EMA2"] = float("NaN")
                    self.pd4hours["EMA3"] = float("NaN")

                    # fill the EMA columns with values
                    somme = 0
                    for i in range(0, ema1period):
                        somme += self.pd4hours.iloc[i][3]
                    SMA = somme / ema1period
                    self.pd4hours.iloc[ema1period - 1, 4] = SMA
                    for i in range(ema1period, len(self.pd4hours['Open'])):
                        self.pd4hours.iloc[i, 4] = (self.pd4hours.iloc[i, 3] * multiplier1) + (
                                    self.pd4hours.iloc[i - 1, 4] * (1 - multiplier1))
                    somme = 0
                    for i in range(0, ema2period):
                        somme += self.pd4hours.iloc[i][3]
                    SMA = somme / ema2period
                    self.pd4hours.iloc[ema2period - 1, 5] = SMA
                    for i in range(ema2period, len(self.pd4hours['Open'])):
                        self.pd4hours.iloc[i, 5] = (self.pd4hours.iloc[i, 3] * multiplier2) + (
                                    self.pd4hours.iloc[i - 1, 4] * (1 - multiplier2))
                    somme = 0
                    for i in range(0, ema3period):
                        somme += self.pd4hours.iloc[i][3]
                    SMA = somme / ema3period
                    self.pd4hours.iloc[ema3period - 1, 6] = SMA
                    for i in range(ema3period, len(self.pd4hours['Open'])):
                        self.pd4hours.iloc[i, 6] = (self.pd4hours.iloc[i, 3] * multiplier3) + (
                                self.pd4hours.iloc[i - 1, 4] * (1 - multiplier3))

                    # backTest
                    buying = False
                    buyPrice = 0
                    K = 1
                    tradeCount = 0
                    for i in range(len(self.pd4hours['Open'])):
                        if (self.pd4hours.iloc[i][4] < self.pd4hours.iloc[i][3]) and \
                                (self.pd4hours.iloc[i][5] < self.pd4hours.iloc[i][3]) and\
                                (self.pd4hours.iloc[i][6] < self.pd4hours.iloc[i][3]) and not buying:
                            buyPrice = self.pd4hours.iloc[i][3]
                            buying = True
                        elif ((self.pd4hours.iloc[i][4] > self.pd4hours.iloc[i][3]) or
                              (self.pd4hours.iloc[i][5] > self.pd4hours.iloc[i][3])
                              or (self.pd4hours.iloc[i][6] > self.pd4hours.iloc[i][3])) and buying:
                            sellPrice = self.pd4hours.iloc[i][3]
                            tradePerf = ((sellPrice - buyPrice) / buyPrice)
                            tradeCount += 1
                            # print('trade n°'+str(tradeCount)+' '+str(tradePerf*100)+' %')
                            K = K * (sellPrice / buyPrice)
                            buying = False
                    stratPerf = (K - 1)*100
                    if stratPerf > bestPerf:
                        bestPerf = stratPerf
                        bestEMA1 = ema1period
                        bestEMA2 = ema2period
                        bestEMA3 = ema3period
                    print('EMA ' + str(ema1period) + ', EMA ' + str(ema2period) + ', EMA ' + str(ema3period) +
                          ' Performance: ' + str("%.2f" % stratPerf) + ' % with ' + str(tradeCount) + ' trades')
        print('Asset Performance from ' + str(self.pd4hours.index[0]) + ' to ' +
              str(self.pd4hours.index[-1]) + ' : ' + str(self.assetPerformance) + ' %')
        print('The best performance is: EMA ' + str(bestEMA1) + ', EMA ' + str(bestEMA2)
              + ', EMA3 ' + str(bestEMA3) + ' ' + str("%.2f" % bestPerf) + ' %')
