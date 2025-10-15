from constants import *
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import os
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("Fetching data.")
    try:
        ccj_data = pd.read_csv(os.path.join(base_dir, DATA_FILE_1), header=2, index_col='Date', parse_dates=True)
        uec_data = pd.read_csv(os.path.join(base_dir, DATA_FILE_2), header=2, index_col='Date', parse_dates=True)
    except FileNotFoundError:
        print("Data files not found. Please run tests.py first.")
        return

    ccj_data.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
    uec_data.columns = ['Close', 'High', 'Low', 'Open', 'Volume']

    if isinstance(ccj_data['Close'], pd.DataFrame):
        ccj_prices = ccj_data['Close'].squeeze()
    else:
        ccj_prices = ccj_data['Close']

    if isinstance(uec_data['Close'], pd.DataFrame):
        uec_prices = uec_data['Close'].squeeze()
    else:
        uec_prices = uec_data['Close']

    # Dropping NaNs
    ccj_prices = ccj_prices.dropna()
    uec_prices = uec_prices.dropna()

    ccj_log_prices = np.log(ccj_prices)
    uec_log_prices = np.log(uec_prices)

    Y = ccj_log_prices
    X = sm.add_constant(uec_log_prices)
    model = sm.OLS(Y, X).fit()
    alpha, beta = model.params

    spread = Y - (alpha + beta * uec_log_prices)

    window = ROLLING_WINDOW_DAYS
    z_score = (spread - spread.rolling(window=window).mean()) / spread.rolling(window=window).std()
    
    signals = pd.DataFrame({
        TICKER_1: ccj_prices,
        TICKER_2: uec_prices,
        'Spread': spread,
        'Z-Score': z_score,
    })
    
    entry = Z_SCORE_ENTRY_THRESHOLD
    exit = Z_SCORE_EXIT_THRESHOLD

    z = signals['Z-Score']
    entry_short = (z.shift(1) <=  entry) & (z >  entry)   # cross above +2 -> short spread
    entry_long  = (z.shift(1) >= -entry) & (z < -entry)   # cross below -2 -> long spread
    exit_cross  = (z.shift(1).abs() >= 0.5) & (z.abs() < 0.5)
    extreme_stop = (z.abs() > EXTREME_STOP)
    exit_on_sign_change = ((z.shift(1) > entry) & (z < 0)) | ((z.shift(1) < -entry) & (z > 0))

    # Create position columns
    signals['Position_A'] = 0
    signals['Position_B'] = 0
    signals['Entry_Flag'] = 0
    signals['Exit_Flag'] = 0

    pos = 0
    position_size = 0.1  # 10% of capital per leg

    for i in range(len(signals)):
        signals['Position_A'] = signals['Position_A'].astype(float)
        signals['Position_B'] = signals['Position_B'].astype(float)
        idx = signals.index[i]
        
        if pos == 0:
            if entry_short.iloc[i]:
                pos = -1
                signals.loc[idx, 'Entry_Flag'] = -1
            elif entry_long.iloc[i]:
                pos = 1
                signals.loc[idx, 'Entry_Flag'] = 1
        
        if pos != 0:
            if exit_cross.iloc[i] or extreme_stop.iloc[i] or exit_on_sign_change.iloc[i]:
                signals.loc[idx, 'Exit_Flag'] = pos
                pos = 0

        # SIMPLIFIED: Equal dollar amounts, opposite directions
        signals.loc[idx, 'Position_A'] = pos * position_size
        signals.loc[idx, 'Position_B'] = -pos * position_size  # Same size, opposite sign

    # filter rows to get entries where entry flag is hold
    # then get z score at entry and it's flag
    true_entries = signals[signals['Entry_Flag'] != 0][['Z-Score', 'Entry_Flag']]
    print("True entries (Z at entry):")
    print(true_entries)

    plt.figure(figsize=(12,6))
    plt.plot(signals['Z-Score'], label='Z-Score')
    plt.axhline(0, color='black', linestyle='--')
    plt.axhline(entry, color='red', linestyle='--')
    plt.axhline(-entry, color='green', linestyle='--')
    plt.scatter(signals.index[signals['Entry_Flag']==1], signals['Z-Score'][signals['Entry_Flag']==1], marker='^', color='green', label='Long Entry')
    plt.scatter(signals.index[signals['Entry_Flag']==-1], signals['Z-Score'][signals['Entry_Flag']==-1], marker='v', color='red', label='Short Entry')
    plt.legend()
    plt.show()


    # Copy the main DataFrame
    df = signals.copy()

    # Calculate daily returns for each stock
    df['ret_A'] = df[TICKER_1].pct_change()
    df['ret_B'] = df[TICKER_2].pct_change()

    transaction_cost = 0.0005
    df['trade_cost'] = transaction_cost * (df['Entry_Flag'].abs())

    # Portfolio return each day = weighted sum of each leg
    df['net_ret'] = df['Position_A'].shift(1) * df['ret_A'] + df['Position_B'].shift(1) * df['ret_B'] - df['trade_cost']

    # Compute cumulative return
    df['cumu_net_ret'] = (1 + df['net_ret']).cumprod() - 1

    plt.figure(figsize=(12,6))
    plt.plot(df['cumu_net_ret'], label='Cumulative Strategy Return')
    plt.title('Pair Trading Strategy Backtest')
    plt.xlabel('Date')
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
    plt.ylabel('Cumulative Return (%)')
    plt.legend()
    plt.show()

    daily_ret = df['net_ret'].dropna()

    sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252)
    total_return = df['cumu_net_ret'].iloc[-1]
    max_drawdown = (df['cumu_net_ret'].cummax() - df['cumu_net_ret']).max()

    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2%}")


    trades = []
    current_pos = 0
    entry_idx = None
    entry_price_A = entry_price_B = None

    for date in df.index:
        z = df.loc[date, 'Z-Score']
        price_A = df.loc[date, TICKER_1]
        price_B = df.loc[date, TICKER_2]
        entry_flag = df.loc[date, 'Entry_Flag']
        exit_flag = df.loc[date, 'Exit_Flag']
        if current_pos == 0 and entry_flag != 0:
            current_pos = entry_flag
            entry_idx = date
            entry_price_A = price_A
            entry_price_B = price_B

        elif current_pos != 0 and exit_flag != 0:
            exit_idx = date
            exit_price_A = price_A
            exit_price_B = price_B
            
            if current_pos == 1:
                # Long A, short B - equal dollar amounts
                trade_return = position_size * ((exit_price_A / entry_price_A - 1) - (exit_price_B / entry_price_B - 1))
            elif current_pos == -1:
                # Short A, long B
                trade_return = position_size * ((entry_price_A / exit_price_A - 1) - (entry_price_B / exit_price_B - 1))
            holding_period = (exit_idx - entry_idx).days
            trades.append((entry_idx, exit_idx, current_pos, trade_return, holding_period))
            current_pos = 0
            entry_idx = None
            entry_price_A = None
            entry_price_B = None
    
    trade_log = pd.DataFrame(trades, columns=['Entry Date', 'Exit Date', 'Direction', 'Return', 'Holding_Period'])
    win_rate = (trade_log['Return'] > 0).mean()
    avg_hold = trade_log['Holding_Period'].mean()
    avg_win = trade_log.loc[trade_log['Return'] > 0, 'Return'].mean()
    avg_loss = trade_log.loc[trade_log['Return'] <= 0, 'Return'].mean()
    expectancy = trade_log['Return'].mean()

    print(f"Win Rate: {win_rate:.2%}")
    print(f"Average Holding Period: {avg_hold:.2f} days")
    print(f"Average Win: {avg_win:.2%}")
    print(f"Average Loss: {avg_loss:.2%}")
    print(f"Expectancy: {expectancy:.2%}")

        # Debug checks (run on your existing df)
    print("Min net_ret:", df['net_ret'].min())
    print("Count days with net_ret <= -1:", (df['net_ret'] <= -1).sum())
    print("Min (1+net_ret):", (1 + df['net_ret']).min())

    # Find the worst day
    worst_day = df['net_ret'].idxmin()
    print(f"\nWorst Day: {worst_day}")
    print(f"Position A: {df.loc[worst_day, 'Position_A']}")
    print(f"Position B: {df.loc[worst_day, 'Position_B']}")
    print(f"Return A: {df.loc[worst_day, 'ret_A']:.2%}")
    print(f"Return B: {df.loc[worst_day, 'ret_B']:.2%}")
    print(f"Net Return: {df.loc[worst_day, 'net_ret']:.2%}")
