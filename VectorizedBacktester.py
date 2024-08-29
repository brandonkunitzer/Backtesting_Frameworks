import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class VectorizedBacktester():
    """
    The purpose of this class is to use vectorized backtesting on trading strategies. With the data and graphing taken care of,
    all the user has to do is define their strategy. This class assumes the trader has the ability to short. However, if the trader can only
    buy shares, they can set 'short' to false in the test strategy functions. The position in each timeframe of the dataframe reflects the position
    based on the current timeframe data. The code in the plot_results function automatically ensures this position is fufilled at the next timeframe
    open so no need to shift position when defining a strategy. For examples of how to define a strategy, check the three examples in the class. Since 
    trading costs vary per broker, they are not accounted for in this program, but should be accounted
    for when designing strategies. 
    """
    def __init__(self, symbol, start, end, interval):
        """
        Parameters
        ----------
        symbol: str
            Symbol or ticker to be backtested
        start: str
            Beginning date of time frame for backtesting
            ex: '2023-1-15' - backtesting will begin on January 15, 2023
        end: str
            End date of time frame for backtesting
            ex: '2024-1-15' - backtesting will end on January 15, 2024
        interval: str
            How often price will be recorded
            ex: '1h' - price will be recorded every hour (equivalent to 1 hour candlestick)
            valid intervals: 1m,2m,5m,15m,30m,1h,1d,5d,1wk,1mo,3mo
            
        """
        self.symbol = symbol
        self.start = pd.to_datetime(start).tz_localize('America/New_York')
        self.end = pd.to_datetime(end).tz_localize('America/New_York')
        self.interval = interval
        self.intraday = False
        if interval[-1] == 'm' or interval[-1] == 'h':
            self.intraday = True
        self.results = pd.DataFrame({})
        self.recent_strategy = ''
        
    def get_data(self):
        """
        Gathers data necessary for backtesting.
        """
        #gather as much of the data as yfinance allows. This is to account
        #for indicators needing historical data in order to start trading at the indicated
        #start date (i.e. an sma of length 30 would return na for the first 29 time periods if
        #the data started at the desired start time)
        cur_day = pd.Timestamp.now().date()
        
        #yfinance only limits how far back intraday periods can go
        if self.intraday == True:
            if self.interval == '1m':
                start_date = (cur_day - pd.DateOffset(days = 6)).tz_localize('America/New_York')
            elif self.interval[-1] == 'm':
                start_date = (cur_day - pd.DateOffset(days = 55)).tz_localize('America/New_York')
            elif self.interval[-1] == 'h':
                start_date = (cur_day - pd.DateOffset(days = 710)).tz_localize('America/New_York')
            #Determine if the entered time period is valid
            if self.start < start_date:
                raise ValueError('Yahoo finance limits how far back {} intrevals can go. Please enter a beginning date after: {}'.format(self.interval, start_date))
            raw = yf.download(tickers = self.symbol, start = start_date, end = self.end, interval = self.interval).copy()
            if raw.index.tz == None:
                raw.index = raw.index.tz_localize('America/New_York')
        else:
            raw = yf.download(tickers = self.symbol, start = self.start - pd.DateOffset(years = 200), end = self.end, interval = self.interval).copy()
            if raw.index.tz == None:
                raw.index = raw.index.tz_localize('America/New_York')
                
        raw = raw[['Open', 'Close', 'Volume']]
        raw.rename(columns = {'Close' : 'price'}, inplace = True)
        raw['returns'] = raw['price'].pct_change()
        raw = raw.dropna()
        return raw
        

    #________________________________Define strategies to test here_____________________________________
                        
    def test_sma_crossover(self, short_sma_window, long_sma_window, short = True):
        """
        Test an SMA crossover strategy where you go long when the shorter sma is above the longer sma and you go short when the    
        shorter sma is below the longer sma.

        Parameters
        ----------
        short_sma_window: int
            legnth of the short sma  
        long_sma_windw: int
            length of the longer sma  
        short: bool
            set to false if unable to take short positions
        """
        results = self.get_data()

        #add indicators
        results['sma{}'.format(short_sma_window)] = results['price'].rolling(short_sma_window).mean()
        results['sma{}'.format(long_sma_window)] = results['price'].rolling(long_sma_window).mean()
       
        #define position
        results['position'] = np.where(results['sma{}'.format(short_sma_window)] > results['sma{}'.format(long_sma_window)], 1, np.nan)
        if short:
            results['position'] = np.where(results['sma{}'.format(short_sma_window)] < results['sma{}'.format(long_sma_window)], -1, results['position'])
        if not short:
            results['position'] = np.where(results['sma{}'.format(short_sma_window)] < results['sma{}'.format(long_sma_window)], 0, results['position'])
        results['position'] = results['position'].ffill()

        #return results
        self.results = results
        #define the this strategy and assign it to the self.recent_startegy varibable
        self.recent_strategy = 'SMA crossover | Short SMA Length: {} | Long SMA Length: {}'.format(short_sma_window, long_sma_window)
        self.plot_results()
        
    def test_bollinger_bands(self, sma_window, deviations, rsi = False, short = True):
        """
        Test a bollinger bands crossover strategy where you go short when price is above the upper band and you wait until price 
        crosses the sma to go neutral. You go long when price is below the lower band and you wait until the price crosses the sma to go neutral.

        Parameters
        ----------
        sma_window: int
            length of the sma used in the bollinger bands
        deviations: int or float
            number of standard deviations away from the sma the upper and lower bands will be
        rsi: bool
            if set to true, longs will only be taken when rsi > 70 and shorts will only be take when rsi < 30
        short: bool
            set to false if unable to take short positions
        """
        results = self.get_data()

        #add indicators
        results['sma{}'.format(sma_window)] = results['price'].rolling(sma_window).mean()
        results['upper_sma{}_std{}'.format(sma_window, deviations)] = results['sma{}'.format(sma_window)] + results['price'].rolling(sma_window).std() * deviations
        results['lower_sma{}_std{}'.format(sma_window, deviations)] = results['sma{}'.format(sma_window)] - results['price'].rolling(sma_window).std() * deviations
        results['diff'] = results['price'] - results['sma{}'.format(sma_window)] #helper column

        window = 14
        results['price_change'] = results['price'].diff() #helper for rsi
        results['gain'] = np.where(results['price_change'] > 0, results['price_change'], 0) #helper for rsi
        results['loss'] = np.where(results['price_change'] < 0, -results['price_change'], 0) #helper for rsi
        avg_gain = results['gain'].rolling(window).mean()
        avg_loss = results['loss'].rolling(window).mean()
        rs = avg_gain / avg_loss
        
        results['rsi'] = 100 - (100 / (1 + rs))

        #define position
        results['position'] = np.where(results['diff'] * results['diff'].shift(1) < 0, 0, np.nan) #price crosses sma - go neutral
        if rsi:
            results['position'] = np.where((results['price'] < results['lower_sma{}_std{}'.format(sma_window, deviations)]) & (results['rsi'] < 30), 1, results['position']) #go long
            if short:
                results['position'] = np.where((results['price'] > results['upper_sma{}_std{}'.format(sma_window, deviations)]) & (results['rsi'] > 70), -1, results['position']) # go short
            if not short:
                results['position'] = np.where((results['price'] > results['upper_sma{}_std{}'.format(sma_window, deviations)]) & (results['rsi'] > 70), 0, results['position'])

        else:
            results['position'] = np.where((results['price'] < results['lower_sma{}_std{}'.format(sma_window, deviations)]), 1, results['position']) # go long
            if short:
                results['position'] = np.where((results['price'] > results['upper_sma{}_std{}'.format(sma_window, deviations)]), -1, results['position']) # go short
            if not short:
                results['position'] = np.where((results['price'] > results['upper_sma{}_std{}'.format(sma_window, deviations)]), 0, results['position'])
        
        results['position'] = results['position'].ffill()
        
        #return results        
        self.results = results
        if rsi:
            self.recent_strategy = 'Bollinger_bands - RSI | SMA Length: {} | STD: {}'.format(sma_window, deviations)
        else:
            self.recent_strategy = 'Bollinger_bands | SMA Length: {} | STD: {}'.format(sma_window, deviations)
        self.plot_results()

    def test_obv_divergence(self, divergence_window = 30, short = True, percent_diff = 0.0):
        """
        Test an On-Balance Volume strategy that takes long and short positions based on divergence in the OBV. For instance, a long is taken when there is 
        a recent low in price, but not in OBV. Similarly, a long is taken when there is a recent high in price, but not in OBV. Go neutral when price 
        crosses the sma that is the length of the divergence window (window for measuring max and mins).

        Parameters
        ----------
        divergence_window: int
            length of window for measuring divergence (max and mins of price and OBV). This is also the sma length
        short: bool
            set to false if unable to take short positions
        """
        results = self.get_data()

        #add indicators
        results['OBV'] = (results['Volume'] * np.sign(results['returns'])).cumsum()
        results['sma{}'.format(divergence_window)] = results['price'].rolling(divergence_window).mean()
        results['diff'] = results['price'] - results['sma{}'.format(divergence_window)]
        results['PMax'] = results['price'].shift(3).rolling(divergence_window).max()
        results['PMin'] = results['price'].shift(3).rolling(divergence_window).min()
        results['CumVMin'] = results['OBV'].shift(3).rolling(divergence_window).min()
        results['CumVMax'] = results['OBV'].shift(3).rolling(divergence_window).max()
        results['Min_diff'] = abs(((results['OBV'] - results['CumVMin']) / results['CumVMin']) * 100)
        results['Max_diff'] = abs(((results['OBV'] - results['CumVMax']) / results['CumVMax']) * 100)
        
       
        #define position
        results['position'] = np.where(results['diff'] * results['diff'].shift(1) < 0, 0, np.nan) # go neutral when price crosses sma
        if short:
            results['position'] = np.where((results['price'] > results['PMax']) & (results['OBV'] < results['CumVMax']) & (results['Max_diff'] > percent_diff), -1, results['position']) # go short
        if not short:
            results['position'] = np.where((results['price'] > results['PMax']) & (results['OBV'] < results['CumVMax']), 0, results['position'])
        results['position'] = np.where((results['price'] < results['PMin']) & (results['OBV'] > results['CumVMin']) & (results['Min_diff'] > percent_diff), 1, results['position']) #go long
        
        results['position'] = results['position'].ffill()

        #return results
        self.results = results
        self.recent_strategy = 'OBV Divergence | Divergence window: {}'.format(divergence_window)
        self.plot_results()
        

    #_______________________________________________________________________________________
            
    def plot_results(self):
        """
        Plot and calculate the results of the trading strategies. This is called after every strategy. The graph displays the approximate value of one dollar invested at the start date.
        """
        if len(self.results) == 0:
            print('Test a Strategy first!')
            return
            
        #change results to desired time frame
        results = self.results.copy()
        results = results.loc[self.start : self.end]
        
        #Adjust first bar to only account for current open
        results.iloc[1, results.columns.get_loc('returns')] = (results.iloc[1]['price'] - results.iloc[1]['Open']) / results.iloc[1]['Open']
        
        #Adjust last bar to only account for the last bar open
        results.iloc[-1, results.columns.get_loc('returns')] = (results.iloc[-1]['Open'] - results.iloc[-2]['price']) / results.iloc[-2]['price']
        
        results['trades'] = results['position'].diff().abs()
        results['strategy'] = results['position'].shift(1) * results['returns']

        #Assume long/short position is taken at the next open, not close
        results['strategy'] = np.where((results['trades'] > 0) & (results['position'].shift(1) != 0), results['position'].shift(1) * ((results['Open'].shift(-1) - results['price'].shift(1)) / results['price'].shift(1)), results['strategy'])
        
        results['strategy'] = np.where((results['trades'].shift(1) > 0) & (results['position'].shift(1) != 0), results['position'].shift(1) * ((results['price'] - results['Open'])/results['Open']), results['strategy'])

        #special case: last row contains a trade
        if results['trades'].iloc[-1] > 0:
            results.iloc[-1, results.columns.get_loc('strategy')] = results['position'].iloc[-2] * results['returns'].iloc[-1]
        
        results = results.dropna()
        results['creturns'] = results['returns'].add(1).cumprod()
        results['cstrategy'] = results['strategy'].add(1).cumprod()
        self.results = results

        #graph results
        if self.recent_strategy != '':
            plt.figure(figsize=(12, 8))
            plt.plot(self.results[['creturns']], label='Buy and hold returns')
            plt.plot(self.results[['cstrategy']], label='Strategy Returns', linestyle='--')
            plt.legend(loc='upper left')
            plt.title('{} | ticker: {} | start: {} | end: {}'.format(self.recent_strategy, self.symbol, self.results.index[0], self.results.index[-1]))
            plt.show()