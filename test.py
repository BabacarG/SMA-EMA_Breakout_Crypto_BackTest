# import relevant libraries
import yfinance as yf
import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import datetime as datetime
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc

yf.pdr_override()  # activate yahoo finance workaround

smasUsed = [10, 30, 50]  # Choose smas

start = dt.datetime(2020, 1, 1) - dt.timedelta(days=max(smasUsed))  # Sets start point of dataframe
now = dt.datetime.now()  # Sets end point of dataframe
stock = input("Enter the stock symbol : ")  # Asks for stock ticker

while stock != "quit":  # Runs this loop until user enters 'quit' (can do many stocks in a row)

    prices = pdr.get_data_yahoo(stock, start, now)  # Fetches stock price data, saves as data frame

    fig, ax1 = plt.subplots()  # Create Plots

    # Calculate moving averages

    for x in smasUsed:  # This for loop calculates the SMAs for the stated periods and appends to dataframe
        sma = x
        prices['SMA_' + str(sma)] = prices.iloc[:, 4].rolling(window=sma).mean()  # calcaulates sma and creates col

    prices["Date"] = mdates.date2num(prices.index)  # creates a date column stored in number format (for OHCL bars)
    ohlc = []  # Create OHLC array which will store price data for the candlestick chart

    # Delete extra dates
    prices = prices.iloc[max(smasUsed):]

    # Go through price history to create candlestics
    for i in prices.index:
        # append OHLC prices to make the candlestick
        append_me = prices["Date"][i], prices["Open"][i], prices["High"][i], prices["Low"][i], prices["Adj Close"][i], \
                    prices["Volume"][i]
        ohlc.append(append_me)

    # plot candlesticks
    candlestick_ohlc(ax1, ohlc, width=.5, colorup='k', colordown='r', alpha=0.75)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # change x axis back to datestamps
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(8))  # add more x axis labels
    plt.tick_params(axis='x', rotation=45)  # rotate dates for readability

    timeD = dt.timedelta(days=30)  # Sets length of dotted line on chart

    plt.xlabel('Date')  # set x axis label
    plt.ylabel('Price')  # set y axis label
    plt.title(stock + " - Daily")  # set title
    plt.ylim(prices["Low"].min(), prices["High"].max() * 1.05)  # add margins
    # plt.yscale("log")

    plt.show()
    # print()
    stock = input("Enter the stock symbol : ")  # Asks for new stock