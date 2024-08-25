import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class IterativeBacktester():
    """
    The purpose of this class is to use event-based backtesting on trading strategies. With the data and graphing taken care of,
    all the user has to do is define their strategy. This class assumes the trader has the ability to short. However, if the trader can only
    buy shares, they can set 'short' to false in the test strategy functions. For examples of how to define a strategy, check the three 
    examples in the class. Since trading costs vary per broker, they are not accounted for in this program, but should be accounted
    for when designing strategies. 
    """
    def __init__(self, symbol, start, end, interval, initial_balance):
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
        intial_balance: int or float
            The initial balance of the account.
            ex: '1000' - account starts with $1000 and the program
            trades with this amount of money
            
        """
        self.symbol = symbol
        self.start = pd.to_datetime(start).tz_localize('America/New_York')
        self.end = pd.to_datetime(end).tz_localize('America/New_York')
        self.interval = interval
        self.intraday = False
        if interval[-1] == 'm' or interval[-1] == 'h':
            self.intraday = True
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.units = 0
        self.position = 0
        
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
            #Determine if the entered time period is valid
            if self.interval == '1m':
                start_date = (cur_day - pd.DateOffset(days = 6)).tz_localize('America/New_York')
            elif self.interval[-1] == 'm':
                start_date = (cur_day - pd.DateOffset(days = 55)).tz_localize('America/New_York')
            elif self.interval[-1] == 'h':
                start_date = (cur_day - pd.DateOffset(days = 710)).tz_localize('America/New_York')
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
        
    def gather_values(self, bar):
        """
        Given a bar, gather the next price and date that trading will occur
        """
        price = self.data.iloc[bar + 1]['Open'] #price is open of the next bar, this is what intrsuments would be bought and sold at
        date = self.data.index[bar + 1].date()
        return price, date
        
    def go_long(self, bar):
        """
        Adjust current balance, position, and units after taking a long trade
        """
        price, date = self.gather_values(bar)
        if self.position == -1:
            self.current_balance -= self.units * price
            self.position = 0
        self.units = self.current_balance / price
        if self.position == 0:
            self.current_balance -= self.units * price
        self.position = 1
        print('{} | Going long at {} | current P&L%: {}'.format(date, price, round(self.calc_cur_pl(bar), 4)))

    def go_short(self, bar):
        """
        Adjust current balance, position, and units after taking a short trade
        """
        price, date = self.gather_values(bar)
        if self.position == 1:
            self.current_balance += self.units * price
            self.position = 0
        self.units = self.current_balance / price
        if self.position == 0:
            self.current_balance += self.units * price
        self.position = -1
        print('{} | Going short at {} | current P&L%: {}'.format(date, price, round(self.calc_cur_pl(bar), 4)))

    def go_neutral(self, bar):
        """
        Adjust current balance, position, and units after going neutral
        """
        price, date = self.gather_values(bar)
        if self.position == -1:
            self.current_balance -= price * self.units 
        if self.position == 1:
            self.current_balance += price * self.units
        self.position = 0
        self.units = 0
        print('{} | Going neutral at {} | current P&L%: {}'.format(date, price, round(self.calc_cur_pl(bar), 4)))

    def end_print(self, bar):
        """
        Determine P&L of strategy and buy and hold and print these values
        """
        price, date = self.gather_values(bar)
        
        pct_change = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
        
        symbol_pct_change = ((self.data.iloc[-1]['Open'] - self.data.iloc[1]['Open']) / self.data.iloc[1]['Open']) * 100
        print('-' * 75)
        print('Final account balance: {} | P&L %: {} | Buy and hold P&L%: {}'.format(round(self.current_balance, 4), round(pct_change, 4), round(symbol_pct_change, 4)))
        print('-' * 75)
        
    def reset_data(self):
        """
        This resets self.data to the desired time frame and resets position, current balance and units
        """
        # reset to current time frame
        self.data = self.data.loc[self.start: self.end]
        self.data = self.data.dropna()
        self.position = 0  # initial neutral position
        self.current_balance = self.initial_balance  # reset initial capital
        self.units = 0
        
    def calc_cur_pl(self,bar):
        """
        Calculate the current P&L based on current balance and initial balance
        """
        price, date = self.gather_values(bar)
        account_balance = self.current_balance
        
        if self.position == 1:
            account_balance += price * self.units
        if self.position == -1:
            account_balance -= price * self.units
            
        return ((account_balance - self.initial_balance) / self.initial_balance) * 100
        
        
    
    #________________________________Define strategies to test here_____________________________________
                        
    def test_sma_crossover(self, short_sma_window, long_sma_window, short = True):
        """
        Test an SMA crossover strategy where you go long when the shorter sma is above the longer sma and you go short when the shorter sma is below the longer sma.
        
        short_sma_window: int
            legnth of the short sma
        long_sma_windw: int
            length of the longer sma
        short: bool
            set to false if unable to take short positions
        """
    
        # nice printout
        stm = "Testing SMA crossover | short sma = {} | long sma = {} | ticker = {}".format(short_sma_window, long_sma_window, self.symbol)
        print('-' * 75)
        print(stm)
        print('-' * 75)

        #refresh self.data
        self.data = self.get_data()

        # add indicators
        self.data['sma{}'.format(short_sma_window)] = self.data["price"].rolling(short_sma_window).mean()
        self.data['sma{}'.format(long_sma_window)] = self.data["price"].rolling(long_sma_window).mean()
        
        # reset to current time frame, must call this before iterating through the dataframe
        self.reset_data()
    
        # define event based strategy
        for bar in range(len(self.data)-2): # all bars (except the last 2 bar)
            # print(self.data.index[bar].date(),self.data.iloc[bar]['Open'], self.data.iloc[bar]['price'], self.calc_cur_pl(bar))
            if self.data['sma{}'.format(short_sma_window)].iloc[bar] > self.data['sma{}'.format(long_sma_window)].iloc[bar]: # go long
                if self.position in [-1,0]:
                    self.go_long(bar)
            elif self.data['sma{}'.format(short_sma_window)].iloc[bar] < self.data['sma{}'.format(long_sma_window)].iloc[bar]: # go short
                if self.position in [0,1]:
                    if short:
                        self.go_short(bar)
                    elif self.position == 1:
                            self.go_neutral(bar)


        self.go_neutral(bar + 1) # close position at the last bars open, the get_values() function takes the open of the next days candle
        self.end_print(bar + 1)

    
    def test_bollinger_bands(self, sma_window, deviations, rsi = False, short = True):
        """
        Test a bollinger bands crossover strategy where you go short when price is above the upper band and you
        wait until price crosses the sma to go neutral. You go long when price is below the lower band and you wait until the
        price crosses the sma to go neutral.
        
        sma_window: int
            length of the sma used in the bollinger bands
        deviations: int or float
            number of standard deviations away from the sma the upper and lower bands will be
        rsi: bool:
            if set to true, longs will only be taken when rsi > 70 and shorts will only be take when rsi < 30
        short: bool
            set to false if unable to take short positions
        """

        # nice printout
        stm = "Testing Bollinger Bands | sma = {} | std = {} | ticker = {}".format(sma_window, deviations, self.symbol)
        print('-' * 75)
        print(stm)
        print('-' * 75)

        #refresh self.data
        self.data = self.get_data()

        # add indicators
        self.data['sma'] = self.data.price.rolling(sma_window).mean()
        self.data['lower'] = self.data.sma - self.data.price.rolling(sma_window).std() * deviations
        self.data['upper'] = self.data.sma + self.data.price.rolling(sma_window).std() * deviations
        self.data['diff'] = self.data.price - self.data.sma #helper for sma crossover

        window = 14
        self.data['price_change'] = self.data['price'].diff() #helper for rsi
        self.data['gain'] = np.where(self.data['price_change'] > 0, self.data['price_change'], 0) #helper for rsi
        self.data['loss'] = np.where(self.data['price_change'] < 0, -self.data['price_change'], 0) #helper for rsi
        avg_gain = self.data['gain'].rolling(window).mean()
        avg_loss = self.data['loss'].rolling(window).mean()
        rs = avg_gain / avg_loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        
        # reset to current time frame, must call this before iterating through the dataframe
        self.reset_data()
    
        # define event based strategy
        for bar in range(len(self.data) - 2):
            if self.data['price'].iloc[bar] < self.data['lower'].iloc[bar]: #go long
                if rsi:
                    if (self.data['rsi'].iloc[bar] < 30) & (self.position in [0, -1]):
                        self.go_long(bar) 
                elif self.position in [0, -1]:
                        self.go_long(bar) 
                    
            elif self.data['price'].iloc[bar] > self.data['upper'].iloc[bar]: #go short
                if short:
                    if rsi:
                        if (self.data['rsi'].iloc[bar] > 70) & (self.position in [0,1]):
                                self.go_short(bar)
                    elif self.position in [0,1]:
                        self.go_short(bar)
                elif self.position == 1:
                    self.go_neutral(bar)
            elif (self.data['diff'].iloc[bar] * self.data['diff'].iloc[bar - 1]) < 0: #go neutral
                if self.position in [1,-1]:
                    self.go_neutral(bar)
        self.go_neutral(bar + 1)
        self.end_print(bar + 1)

    def test_obv_divergence(self, divergence_window = 30, short = True, percent_diff = 0):
        """
        Test an On-Balance Volume strategy that takes long and short positions based on divergence in the OBV. For instance, a long is taken when there is 
        a recent low in price, but not in OBV. Similarly, a long is taken when there is a recent high in price, but not in OBV. Go neutral when price 
        crosses the sma that is the length of the divergence window (window for measuring max and mins).
        
        divergence_window: int
            length of window for measuring divergence (max and mins of price and OBV). This is also the sma length
        short: bool
            set to false if unable to take short positions
        """
        stm = "Testing OBV divergence | Divergence window = {} | ticker = {}".format(divergence_window, self.symbol)
        print('-' * 75)
        print(stm)
        print('-' * 75)

        #refresh self.data
        self.data = self.get_data()

        # add indicators
        self.data['OBV'] = (self.data['Volume'] * np.sign(self.data['returns'])).cumsum()
        self.data['sma{}'.format(divergence_window)] = self.data['price'].rolling(divergence_window).mean()
        self.data['diff'] = self.data['price'] - self.data['sma{}'.format(divergence_window)]
        self.data['PMax'] = self.data['price'].shift(3).rolling(divergence_window).max()
        self.data['PMin'] = self.data['price'].shift(3).rolling(divergence_window).min()
        self.data['CumVMin'] = self.data['OBV'].shift(3).rolling(divergence_window).min()
        self.data['CumVMax'] = self.data['OBV'].shift(3).rolling(divergence_window).max()
        self.data['Min_diff'] = abs(((self.data['OBV'] - self.data['CumVMin']) / self.data['CumVMin']) * 100)
        self.data['Max_diff'] = abs(((self.data['OBV'] - self.data['CumVMax']) / self.data['CumVMax']) * 100)
        
        # reset to current time frame, must call this before iterating through the dataframe
        self.reset_data()
        
        # define event based strategy
        for bar in range(len(self.data) - 2):
            #go short
            if (self.data['price'].iloc[bar] > self.data['PMax'].iloc[bar]) & (self.data['CumVMax'].iloc[bar] > self.data['OBV'].iloc[bar]) & (self.data['Max_diff'].iloc[bar] > percent_diff):
                if self.position in [0,1]:
                    if short:
                        self.go_short(bar)
                    elif self.position == 1:
                        self.go_neutral(bar)
            #go long
            elif (self.data['price'].iloc[bar] < self.data['PMin'].iloc[bar]) & (self.data['CumVMin'].iloc[bar] < self.data['OBV'].iloc[bar]) & (self.data['Min_diff'].iloc[bar] > percent_diff):
                if self.position in [0,-1]:
                    self.go_long(bar)
            elif (self.data['diff'].iloc[bar] * self.data['diff'].shift(1).iloc[bar] < 0): #go neutral
                if self.position in [-1,1]:
                    self.go_neutral(bar)
            
        self.go_neutral(bar + 1)
        self.end_print(bar + 1)





