from binance.client import Client
import csv
import datetime
import pandas as pd
import mplfinance as mpf


class CryptoBackTest:
    def __init__(self, asset, timeFrame, startDate):
        print("Collecting Data...")
        api_key = ''
        api_secret = ''
        client = Client(api_key, api_secret)
        self.assetTicker = asset
        self.bestPeriod = 0
        binanceTimeFrame = ""

        if timeFrame == "1min":
            binanceTimeFrame = Client.KLINE_INTERVAL_1MINUTE
        elif timeFrame == "3min":
            binanceTimeFrame = Client.KLINE_INTERVAL_3MINUTE
        elif timeFrame == "5min":
            binanceTimeFrame = Client.KLINE_INTERVAL_5MINUTE
        elif timeFrame == "15min":
            binanceTimeFrame = Client.KLINE_INTERVAL_15MINUTE
        elif timeFrame == "30min":
            binanceTimeFrame = Client.KLINE_INTERVAL_30MINUTE
        elif timeFrame == "1h":
            binanceTimeFrame = Client.KLINE_INTERVAL_1HOUR
        elif timeFrame == "2h":
            binanceTimeFrame = Client.KLINE_INTERVAL_2HOUR
        elif timeFrame == "4h":
            binanceTimeFrame = Client.KLINE_INTERVAL_4HOUR
        elif timeFrame == "6h":
            binanceTimeFrame = Client.KLINE_INTERVAL_6HOUR
        elif timeFrame == "8h":
            binanceTimeFrame = Client.KLINE_INTERVAL_8HOUR
        elif timeFrame == "12h":
            binanceTimeFrame = Client.KLINE_INTERVAL_12HOUR
        elif timeFrame == "1d":
            binanceTimeFrame = Client.KLINE_INTERVAL_1DAY
        elif timeFrame == "3d":
            binanceTimeFrame = Client.KLINE_INTERVAL_3DAY
        elif timeFrame == "1w":
            binanceTimeFrame = Client.KLINE_INTERVAL_1WEEK
        elif timeFrame == "1m":
            binanceTimeFrame = Client.KLINE_INTERVAL_1MONTH

        # return: Open time,Open,High,Low,Close,Volume,Close time,Quote asset volume,Number of trades,
        # Taker buy base asset,Taker buy quote asset volume,Ignore.
        candles = client.get_historical_klines(asset, binanceTimeFrame, startDate)
        csvfile = open('OHLC.csv', 'w', newline='')
        candlestick_writer = csv.writer(csvfile, delimiter=',')

        for candlestick in candles:
            candlestick_writer.writerow(candlestick)

        # convert csv into dataframe to plot
        self.pdOHLC = pd.read_csv('OHLC.csv', index_col=False, parse_dates=True, header=None, quoting=csv.QUOTE_NONE)

        # convert epoch time to DateTime
        for i in range(len(self.pdOHLC[0])):
            epoch = int(self.pdOHLC.iloc[i][0]) / 1000
            date_time = datetime.datetime.fromtimestamp(epoch)
            self.pdOHLC.at[i, 0] = date_time

        # give column names
        self.pdOHLC.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                               'Number of trades', 'Taker buy base asset', 'Taker buy quote asset volume', 'Ignore']

        # drop useless columns
        self.pdOHLC.drop(columns=['Volume', 'Close time', 'Quote asset volume', 'Number of trades',
                                  'Taker buy base asset', 'Taker buy quote asset volume', 'Ignore'], inplace=True)

        # put datetime as index
        self.pdOHLC.set_index('Date', inplace=True)
        # csvfile.close()
        print("Data collected")

    def buysell1sma(self, start, end):
        print('Processing the backtest from ' + str(self.pdOHLC.index[end]))

        # BackTest with 1 SMA Buying and Selling
        bestPerf = -101
        self.bestPeriod = 0
        bestSMADD = 0
        bestSMAnt = 0
        bestSTA = 0
        bestBTA = 0
        bestWTA = 0
        bestLTA = 0
        bestChart = self.pdOHLC.copy(deep=True)
        for smaperiod in range(start, end + 1):
            # creation and calculation for SMA
            self.pdOHLC["SMA"] = float("NaN")
            self.pdOHLC["Equity"] = float("NaN")
            self.pdOHLC["SMA"] = self.pdOHLC["Close"].rolling(smaperiod).mean()
            # sma strategy backTest
            buying = False
            selling = False
            maxDrawdown = 0
            top = 0
            buyPrice = 0
            sellPrice = 0
            K = self.pdOHLC.iloc[end-1][3]
            tradeCount = 0

            sellingTradesSum = 0
            buyingTradesSum = 0
            winningTradesSum = 0
            losingTradesSum = 0
            sellingTradesCount = 0
            buyingTradesCount = 0
            winningTradesCount = 0
            losingTradesCount = 0

            for i in range(end-1, len((self.pdOHLC['Open']))):
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
                self.bestPeriod = smaperiod
                bestSMADD = maxDrawdown
                bestSMAnt = tradeCount
                bestSTA = sellingTradesAvg
                bestBTA = buyingTradesAvg
                bestWTA = winningTradesAvg
                bestLTA = losingTradesAvg
                bestChart = self.pdOHLC.copy(deep=True)

            print('SMA ' + str(smaperiod) + ' Performance: ' + str(stratPerf) + ' % with ' +
                  str(tradeCount) + ' trades, Max Drawdown: ' + str(maxDrawdown))
        firstValue = self.pdOHLC.iloc[end][3]
        lastValue = self.pdOHLC.iloc[len(self.pdOHLC['Open']) - 1][3]
        assetPerformance = "%.2f" % (((lastValue - firstValue) / firstValue) * 100)

        print(" ")
        print(self.assetTicker + ' performance from ' + str(self.pdOHLC.index[end]) + ' to '
              + str(self.pdOHLC.index[-1]) + ' : ' + str(assetPerformance) + ' %')
        print(" ")

        print('The best performance is SMA ' + str(self.bestPeriod) + ': ' + str("%.2f" % bestPerf) + ' %')
        print('Number of trades: ' + str(bestSMAnt))
        print('Max Drawdown: ' + str("%.2f" % bestSMADD) + ' %')
        print('Winning trades average: ' + str("%.2f" % (bestWTA * 100)) + ' %')
        print('Losing trades average: ' + str("%.2f" % (bestLTA * 100)) + ' %')
        print('Buying trades average: ' + str("%.2f" % (bestBTA * 100)) + ' %')
        print('Selling trades average: ' + str("%.2f" % (bestSTA * 100)) + ' %')

        self.pdOHLC = bestChart
        self.plot()

    def buysell1ema(self, start, end):
        print('Processing the backtest from ' + str(self.pdOHLC.index[end]))

        # BackTest with 1 EMA Buying and Selling
        bestPerf = -101
        self.bestPeriod = 0
        bestEMADD = 0
        bestEMAnt = 0
        bestSTA = 0
        bestBTA = 0
        bestWTA = 0
        bestLTA = 0
        bestChart = self.pdOHLC.copy(deep=True)
        for emaperiod in range(start, end + 1):
            # creation and calculation for SMA
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
            self.pdOHLC["Equity"] = float("NaN")
            buying = False
            selling = False
            maxDrawdown = 0
            top = 0
            buyPrice = 0
            sellPrice = 0
            K = self.pdOHLC.iloc[end-1][3]
            tradeCount = 0

            sellingTradesSum = 0
            buyingTradesSum = 0
            winningTradesSum = 0
            losingTradesSum = 0
            sellingTradesCount = 0
            buyingTradesCount = 0
            winningTradesCount = 0
            losingTradesCount = 0

            for i in range(end-1, len((self.pdOHLC['Open']))):
                currentPrice = self.pdOHLC.iloc[i][3]
                currentEMA = self.pdOHLC.iloc[i][4]
                if (currentEMA < currentPrice) and (not buying):
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
                elif (currentEMA > currentPrice) and (not selling):
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
                self.bestPeriod = emaperiod
                bestEMADD = maxDrawdown
                bestEMAnt = tradeCount
                bestSTA = sellingTradesAvg
                bestBTA = buyingTradesAvg
                bestWTA = winningTradesAvg
                bestLTA = losingTradesAvg
                bestChart = self.pdOHLC.copy(deep=True)

            print('EMA ' + str(emaperiod) + ' Performance: ' + str(stratPerf) + ' % with ' +
                  str(tradeCount) + ' trades, Max Drawdown: ' + str(maxDrawdown))
        firstValue = self.pdOHLC.iloc[end][3]
        lastValue = self.pdOHLC.iloc[len(self.pdOHLC['Open']) - 1][3]
        assetPerformance = "%.2f" % (((lastValue - firstValue) / firstValue) * 100)

        print(" ")
        print(self.assetTicker + ' performance from ' + str(self.pdOHLC.index[end]) + ' to '
              + str(self.pdOHLC.index[-1]) + ' : ' + str(assetPerformance) + ' %')
        print(" ")

        print('The best performance is EMA ' + str(self.bestPeriod) + ': ' + str("%.2f" % bestPerf) + ' %')
        print('Number of trades: ' + str(bestEMAnt))
        print('Max Drawdown: ' + str("%.2f" % bestEMADD) + ' %')
        print('Winning trades average: ' + str("%.2f" % (bestWTA * 100)) + ' %')
        print('Losing trades average: ' + str("%.2f" % (bestLTA * 100)) + ' %')
        print('Buying trades average: ' + str("%.2f" % (bestBTA * 100)) + ' %')
        print('Selling trades average: ' + str("%.2f" % (bestSTA * 100)) + ' %')

        self.pdOHLC = bestChart
        self.plot()

    def plot(self):
        if ('EMA' in self.pdOHLC.columns) and ('Equity' in self.pdOHLC.columns):
            otherPlots = [mpf.make_addplot(self.pdOHLC['EMA'], color='g', secondary_y=False),
                          mpf.make_addplot(self.pdOHLC['Equity'], secondary_y=False)]
            self.assetTicker = self.assetTicker + " (Candlestick), EMA "+str(self.bestPeriod)+"(Green), Equity (Blue)"
        elif ('SMA' in self.pdOHLC.columns) and ('Equity' in self.pdOHLC.columns):
            otherPlots = [mpf.make_addplot(self.pdOHLC['SMA'], color='g', secondary_y=False),
                          mpf.make_addplot(self.pdOHLC['Equity'], secondary_y=False)]
            self.assetTicker = self.assetTicker + " (Candlestick), SMA "+str(self.bestPeriod)+"(Green), Equity (Blue)"
        elif 'EMA' in self.pdOHLC.columns:
            otherPlots = mpf.make_addplot(self.pdOHLC['EMA'], color='g', secondary_y=False)
            self.assetTicker = self.assetTicker + " (Candlestick), EMA "+str(self.bestPeriod)+"(Green)"
        elif 'SMA' in self.pdOHLC.columns:
            otherPlots = mpf.make_addplot(self.pdOHLC['SMA'], color='g', secondary_y=False)
            self.assetTicker = self.assetTicker + " (Candlestick), SMA "+str(self.bestPeriod)+"(Green)"
        elif 'Equity' in self.pdOHLC.columns:
            otherPlots = mpf.make_addplot(self.pdOHLC['Equity'], secondary_y=False)
            self.assetTicker = self.assetTicker + " (Candlestick), Equity (Blue)"
        else:
            data = pd.DataFrame()
            otherPlots = mpf.make_addplot(data)
        mpf.plot(self.pdOHLC, type='candle', style='binance', datetime_format='%d-%m-%Y', warn_too_much_data=99000,
                 addplot=otherPlots, scale_width_adjustment=dict(lines=0.85), title=self.assetTicker,
                 ylabel="Price")
