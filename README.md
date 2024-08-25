# Backtesting Frameworks
## Vectorized and Event Based Backtesting Engines

These two projects were created to provide a frameowrk for backtesting trading strategies. As long as rules for a strategy can be defined, then it can be backtested using either the vectorized or iterative (event-based) backtesting framework. This project was created with the following goals:

* To enable easy and free backtesting for any trading strategy
* Graphing results of strategies


### Vectorized backtester in action:
<img width="1256" alt="Screenshot 2024-08-25 at 12 21 11 AM" src="https://github.com/user-attachments/assets/c45816dc-b073-41b0-8141-72aabf5bea38">

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
        2) See results with currency <br />
    </td>
 </tr>
</table>

### Steps for using class:









