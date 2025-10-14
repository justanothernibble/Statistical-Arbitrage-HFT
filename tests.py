"""import os
import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import math
import numpy as np
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt"""

from scipy.stats import zscore


def run_tests():
    import yfinance as yf
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import coint
    import matplotlib.pyplot as plt
    import os

    # Get the directory of the current file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cached = False

    # check if the data is cached
    if os.path.exists(os.path.join(base_dir, 'ccj_data.csv')) and os.path.exists(os.path.join(base_dir, 'uec_data.csv')):
        cached = True

    # Step 1: Download the data for CCJ and UEC
    if cached == False:
        print("Existing files Not Found. Downloading data...")
        start_date = '2010-01-01'
        end_date = '2025-01-01'

        # Download CCJ and UEC stock data from Yahoo Finance
        print("Downloading CCJ data...")
        ccj_data = yf.download('CCJ', start=start_date, end=end_date, progress=False)
        print("Downloading UEC data...")
        uec_data = yf.download('UEC', start=start_date, end=end_date, progress=False)
        
        # Data is not cached, so store in CSV
        ccj_data.to_csv(os.path.join(base_dir, 'ccj_data.csv'))
        uec_data.to_csv(os.path.join(base_dir, 'uec_data.csv'))
        cached = True
    else:
        print("Existing files Found. Loading data...")
        # Data is cached, so load from CSV
        ccj_data = pd.read_csv(os.path.join(base_dir, 'ccj_data.csv'), header=2, index_col='Date', parse_dates=True)
        uec_data = pd.read_csv(os.path.join(base_dir, 'uec_data.csv'), header=2, index_col='Date', parse_dates=True)
    
    # Step 1.1:
    # Rename columns to match expected format
    ccj_data.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
    uec_data.columns = ['Close', 'High', 'Low', 'Open', 'Volume']

    # Step 2: Extract the 'Close' prices - handle multi-index columns
    # Use .squeeze() to convert DataFrame to Series if needed

    # Absolute prices for close price graph
    if isinstance(ccj_data['Close'], pd.DataFrame):
        ccj_prices = ccj_data['Close'].squeeze()
    else:
        ccj_prices = ccj_data['Close']
    
    if isinstance(uec_data['Close'], pd.DataFrame):
        uec_prices = uec_data['Close'].squeeze()
    else:
        uec_prices = uec_data['Close']

    # Step 3: Ensure there are no missing values (NaNs) in both series
    ccj_prices = ccj_prices.dropna()
    uec_prices = uec_prices.dropna()

    # Step 4: Log prices for spread and cointegration test
    if isinstance(ccj_data['Close'], pd.DataFrame):
        ccj_log_prices = np.log(ccj_data['Close'].squeeze())
    else:
        ccj_log_prices = np.log(ccj_data['Close'])

    if isinstance(uec_data['Close'], pd.DataFrame):
        uec_log_prices = np.log(uec_data['Close'].squeeze())
    else:
        uec_log_prices = np.log(uec_data['Close'])



    # Align all 4 series based on their date index
    ccj_prices, uec_prices = ccj_prices.align(uec_prices, join='inner')
    ccj_log_prices, uec_log_prices = ccj_log_prices.align(uec_log_prices, join='inner')

    # Verify we have data
    print(f"CCJ prices shape: {ccj_prices.shape}")
    print(f"UEC prices shape: {uec_prices.shape}")
    print(f"Date range: {ccj_prices.index[0]} to {ccj_prices.index[-1]}")

    # Step 4.5: Perform the cointegration test (Engle-Granger)
    score, p_value, _ = coint(ccj_log_prices, uec_log_prices)

    # Step 5: Interpret the result
    print(f'\nCointegration Test p-value: {p_value:.6f}')
    if p_value < 0.05:
        print("The series are cointegrated!")
    else:
        print("The series are not cointegrated.")
    
    Y = ccj_log_prices
    X = sm.add_constant(uec_log_prices)
    model = sm.OLS(Y, X).fit()
    alpha, beta = model.params
    print(f"Alpha: {alpha:.4f}, Beta: {beta:.4f}")

    # 5. Spread (residuals)
    # Only use the price series, not the full X matrix
    spread = Y - (alpha + beta * uec_log_prices)    
    print(f"Spread: {spread}")

    # Step 6: Plot the two time series to visualize their relationship
    plt.figure(figsize=(12, 5))
    plt.plot(ccj_prices.index, ccj_prices.values, label='CCJ', color='blue', linewidth=1)
    plt.plot(uec_prices.index, uec_prices.values, label='UEC', color='green', linewidth=1)
    plt.legend(loc='best')
    plt.title('CCJ vs UEC Stock Prices')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Plot the spread with rolling mean and standard deviation
    window = 60
    spread_rolling_mean = spread.rolling(window=window).mean()
    spread_rolling_std = spread.rolling(window=window).std()

    plt.figure(figsize=(12, 5))
    # Plots the spread's values and each corresponding date, with colour purple and line width 1
    plt.plot(spread.index, spread.values, label='Spread: CCJ - UEC', color='purple', linewidth=1)
    # Plots a horizontal line at the mean of the spread, with colour red and line width 1
    plt.plot(spread.index, spread_rolling_mean, color='red', linestyle='--', label=f'{window}-Day Rolling Mean', linewidth=1)
    # Plots horizontal lines at the mean plus and minus 2 standard deviations of the spread, with colour orange and line width 1
    plt.plot(spread.index, spread_rolling_mean + 2*spread_rolling_std, 
            color='orange', linestyle=':', label=f'{window}-Day +2 Std Dev', linewidth=1)
    plt.plot(spread.index, spread_rolling_mean - 2*spread_rolling_std, 
            color='orange', linestyle=':', label=f'{window}-Day -2 Std Dev', linewidth=1)

    plt.title('Spread: CCJ - UEC (with Rolling Mean and ±2 Std Dev)')
    plt.xlabel('Date')
    plt.ylabel('Spread')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    print("Now calculating signals...")

    z_score = (spread - spread.rolling(window=window).mean()) / spread.rolling(window=window).std()    
    signals = pd.DataFrame({
        'CCJ': ccj_prices,
        'UEC': uec_prices,
        'Spread': spread,
        'Z-Score': z_score,
    })
    print(signals.tail())

    print("Visualising Z-Score Vs Spread...")
    plt.figure(figsize=(12, 6))
    plt.plot(signals['Z-Score'], label='Z-Score')
    plt.axhline(0, color='black', linestyle='--')
    plt.axhline(2, color='red', linestyle='--')
    plt.axhline(-2, color='green', linestyle='--')
    plt.title('Z-Score of CCJ vs UEC Spread')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()