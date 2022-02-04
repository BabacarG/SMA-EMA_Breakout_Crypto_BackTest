## SMA-EMA_Breakout_Strategy_BackTest
  A tool connected to the binance API to determine which moving average period is the most optimal to use for a given cryptocurrency.

  Warning: This is not investment advice.
  
  This python script is a tool to compare the past performances of a well known trading strategy applied to 
  cryptocurrencies. The strategy is the Moving Average breakout strategy. You will find below links to explanations of 
  the operating principles of the concepts mentioned. This strategy consists of calculating a moving average of period x
  and buying the asset when the price goes above the moving average and selling when the price goes below. What is 
  interesting here is to determine which of the moving average periods is the most profitable. You can therefore enter a
  range of periods to compare. You can also choose to use either the Simple Moving Average (SMA) or the Exponential 
  Moving Average (EMA). Market price data is pulled from Binance API. The results of the backtest will be printed in the
  console and a graph of the asset price will be displayed with the equity curve in blue and the EMA/SMA in green. The 
  starting capital is fixed at the price of the asset at the start of the backtest. This means that if the equity curve 
  is above the price of the asset you outperform the asset and vice versa. Transaction fees are not simulated.
  
  In my opinion, a good way to improve this strategy should be to add money management rules.
  
  # Settings you can change:
  - Whether you will use EMA or SMA
  - Timeframe (1 week, 1 day, 1 minute etc...)
  - The asset (Any asset provided by Binance)
  - The range of SMA/EMA periods you want to compare
  - The start date of the backtest
  
  (Note that the date you choose will be shifted by: (higherSMA/EMA * Timeframe). Exemple: I choose the backtest to 
  start the 1st of january 2020, my higher SMA/EMA to compare is the SMA/EMA with a period of 80 and the timeframe is 
  daily. Then the start date will be delayed by higherSMA/EMA * Timeframe = 80 * 1 day = 80 days. The strategy will
  therefore be applied from March 21, 2020. The start date of Binance data may also affect the start date of the 
  backtest.)

  # Requirements to run this script:
  - Pip install the required packages

  # Reach me out:
  - gueye.bv@hotmail.com
  - https://www.linkedin.com/in/babacar-gueyeesigelec/
  
  # Some documentation about technical analysis:
  - https://www.investopedia.com/terms/o/ohlcchart.asp
  - https://www.investopedia.com/terms/t/technicalanalysis.asp
  - https://www.investopedia.com/terms/s/sma.asp
  - https://www.investopedia.com/terms/e/ema.asp
