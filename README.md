# Statistical Arbitrage High-Frequency Trading Model

this shit isnt even hft because its only backtested, im just trying to sound impressive.

this took me about 20 hours to make. ai barely understood this shit so i had to figure this out by myself.

the model compares two uranium stocks, ccj (cameco corp) and uec (uranium energy corp).

if you want to test it, clone the repo then run app.py. you can change the stocks if you want in constants.py

## how it works
ill explain how it works now.

### quick diagram
+-------------------------------+
|      Statistical Model        |
| (Cointegration, Spread, Z)    |
+-------------------------------+
               ↓
+-------------------------------+
|      Signal Generation        |
| (Crosses, Entry/Exit flags)   |
+-------------------------------+
               ↓
+-------------------------------+
|     Position Management       |
| (Long/Short state machine)    |
+-------------------------------+
               ↓
+-------------------------------+
|      Risk Management          |
| (Stops, sizing, limits)       |
+-------------------------------+
               ↓
+-------------------------------+
|   Performance Tracking        |
| (Sharpe, drawdown, win rate)  |
+-------------------------------+

### statistical model
the model uses cointegration to find the relationship between the two stocks. it then uses the spread to find the z score of the spread. the z score is then used to generate signals.

### signal generation
the model uses crosses to generate signals. it uses a rolling window to calculate the z score. it then uses the z score to generate signals. the signals are then used to generate trades.

### position management
the model uses a long/short state machine to manage positions. it uses a simple position sizing method to size positions. it then uses the position sizing method to generate trades.

### risk management
the model uses a simple risk management method to manage risk. it uses a simple position sizing method to size positions. it then uses the position sizing method to generate trades.

### performance tracking
the model uses a simple performance tracking method to track performance. it uses a simple position sizing method to size positions. it then uses the position sizing method to generate trades.

## results

so what actually happend? well, here is the output:

```
Total Return: 27.92%
Sharpe Ratio: 0.41
Max Drawdown: 10.26%
Win Rate: 80.77%
Average Holding Period: 30.47 days
Average Win: 0.87%
Average Loss: -2.03%
Expectancy: 0.31%
```

as you can see, it wasnt that great. but it was a learning experience.

## screenshots
![prices](ccj_uec_prices.png)
![spread with rolling mean](ccj_uec_spread_rolling_mean.png)
![z score of spread](ccj_uec_z_score_of_spread.png)
![entry signals](stat_arb_signals.png)
![cumulative returns](stat_arb_cumulative_returns.png)
