# Backtesting Frameworks
## Vectorized and Event Based Backtesting Engines

These two projects were created to provide a framework for backtesting trading strategies. As long as rules for a strategy can be defined, then it can be backtested using either the vectorized or iterative (event-based) backtesting framework. This project was created with the following goals:

* To enable easy and free backtesting for any trading strategy
* Displaying results of strategies


### Vectorized backtester in action:
<img width="1100" alt="Screenshot 2024-08-29 at 12 56 53 PM" src="https://github.com/user-attachments/assets/04f74243-bc8f-4c96-a596-58827970ce23">

### Event based backtester in action:
<img width="661" alt="Screenshot 2024-08-25 at 12 22 05 AM" src="https://github.com/user-attachments/assets/457783dc-3f82-486c-935b-f62e9155e348">

### Technicals
Both frameworks were developed in python. I used yfinance as a source of the financial data. Other packages I used were numpy, pandas, and matplotlib. The user is able to enter a desired start date, but the progrma is designed to fetch as much data as possible before this start date so that it can develop indicators by the start for date. For instance, if someone wanted to test a startegy that included a 200 day simple moving average, then they would need 200 time frames of data before their desired start date in order to begin backtesting on that date. However, let it be known that it is not always possible to gather enough data due to yfinance restrictions. For both frameworks, decisions are made based on the current position, then executed at the next open. For example, if based on some indicators that were implemented, a short position was determined, then that trade would take place on the next day's open. This is built into the frameworks and does not need to be accounted for. Additionally, for all of the example strategies I have implemented, there is an option to eliminate shorting positions. I know shorting a stock is not an option for everyone, so there is an option to only go long in each strategy. Returns in the vectorized strategy are calculated by taking the cummulative product of the returns (percent differences between last price and current). Returns for the event-based backtester are calculated through an initial balance that the user inputs. Both startegies can access multiple different timeframes (i.e. 1m, 2m, 5m, 15m, 30m, 1h, 1d, etc.)

### Differences between the two frameworks:
<table border="0">
 <tr>
    <td><b style="font-size:30px">Vectorized backtester</b></td>
    <td><b style="font-size:30px">Event-based backtester</b></td>
 </tr>
 <tr>
    <td>1) Quicker calculations <br />
        2) Graphing of results<br />
        3) Easier to implement strategies <br />
    </td>
    <td>1) Test more complex strategies <br />
        2) See results with actual currency <br />
        3) More accurate results <br />
    </td>
 </tr>
</table>

### Steps for using class:

Step 1) Download all included .py files and add to the same folder. <br />
Step 2) If not done already, pip install yfinance, numpy, pandas, matplotlib <br />
Step 3a) For vectorized backtester, open 'running_vectorized_backtester.py' in a code editor <br />
Step 3b) For iterative backtester, open 'running_iterative_backtester.py' in a code editor <br />
Step 4) Edit parameters as desired and comment out the strategies you do not want to run. I included an example of running each startegy that I coded <br />
Step 5) Run the code and analyze results! <br />

### Steps for developing a strategy:

Step 1a) To develop a vectorized strategy, open 'VectorizedBacktester.py' in a code editor. <br />
Step 1b) To develop an event-based strategy, open 'IterativeBacktester.py' in a code editor. <br />
Note) I reccommend using jupyter lab or another IDE <br />
<br />
Step 2) Scroll down to each section that says 'Define strategies to test here' <br />
Step 3) Copy and paste one of the exissting test_'strategy' functions <br />
<br />
#### Vectorized
Step 4a) For a vectorized strategy, define the indicators you will need for your strategy under the comment 'add indicators'. Add the indicators as columns to the pandas dataframe 'results'. You will have to manually calculate all indicators. For example for a 200 day simple moving average, the code looks like: results['sma200'] = results['price'].rolling(200).mean() 
<br />
Note) results['price'] will access the close prices for each timeframe <br />
<br />
Step 5a) Define position based on the indicators under the comment 'define position'. Here, assign positions to the column 'position' so results['position']. This ensures the code will run correctly. To assign a long position for a bar/timeframe the position column should be of the value 1, for a short position it should be -1 and for neutral it should be 0. Assigning positions is usually done with np.where(condition(i.e. sma50 > sma 200), 1 (what results['position'] should be set to if condition is true), results['position'] (what it should be set to if the condition is false)) <br />
<br />
Step  6a) Under the comment 'return results', only change the code that is assigning self.recent_strategy. You should change this varible to a string with information about the strategy you developed <br />
<br />
Step 7a) Run the code and verify that your strategy is buying/selling when you want it too. If you are using an IDE, you can call 'backtester.results' to see the dataframe with the indicators, position, prices, etc. to verify the results <br />
<br />
#### Event-based
Step 4b) For an event-based strategy, define the indicators you will need for your strategy under the comment 'add indicators'. Add the indicators as columns to the pandas dataframe self.data. You will have to manually calculate all indicators. For example for a 200 day simple moving average, the code looks like: self.data['sma200'] = self.data['price'].rolling(200).mean() <br />
Note) results['price'] will access the close prices for each timeframe <br />
<br />
Step 5b) Define strategy based on the indicators under the comment 'define event based strategy'. Here use the loop to either go long or go short at each price. Use self.data['price'].iloc[bar] to access the price at each timeframe.  <br />
<br />
Step 6b) After defining the strategy DO NOT remove the last two lines of the function (i.e. 'self.go_neutral(bar + 1)' and 'self.end_print(bar + 1)') <br />
<br />
Step 7b) Run the code and verify that your strategy is buying/selling when you want it too. If you are using an IDE, you can call 'backtester.data' to see the dataframe with the indicators, position, prices, etc. to verify the results <br />

### DISCLAIMER
As trading costs vary per broker/trade, I did not include a method for adding trading costs. However, before considering trading a strategy it is always important to account for trading costs. It is not too difficult to add them as you need to change some code in either the plot_results() function for vectorized or the go_long(), go_shot(), and go_neutral() methods. Additionally, neither I nor the tool are providing investment advice.

















