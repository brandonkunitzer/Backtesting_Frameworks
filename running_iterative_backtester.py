#import iterative backtester class by saved name
import IterativeBacktester_copy as IB

#Create an instance of the class. Change dates, ticker, timeframe, account_balance etc.
# With some timeframes, you can only go back so far. Trying to go back too far will fetch an error that describes how far you can go back
backtester = IB.IterativeBacktester('SPY', '2022-1-1', '2023-1-1', '1d', 1000)

#backtest whichever strategy you want to.
#Change parameters to experiment with different strategies. Check docstrings for parameter information
backtester.test_sma_crossover(50,200, short = False)
backtester.test_bollinger_bands(30,2, rsi = True)
backtester.test_obv_divergence()