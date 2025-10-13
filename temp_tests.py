"""import yfinance as yf
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt

# Step 1: Download the data for KO and PEP
start_date = '2010-01-01'
end_date = '2023-01-01'

# Download KO and PEP stock data from Yahoo Finance
print("Downloading CCJ data...")
ccj_data = yf.download('CCJ', start=start_date, end=end_date, progress=False)
print("Downloading UEC data...")
uec_data = yf.download('UEC', start=start_date, end=end_date, progress=False)

# Step 2: Extract the 'Close' prices - handle multi-index columns
# Use .squeeze() to convert DataFrame to Series if needed
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

# Align both series based on their date index
ccj_prices, uec_prices = ccj_prices.align(uec_prices, join='inner')

# Verify we have data
print(f"CCJ prices shape: {ccj_prices.shape}")
print(f"UEC prices shape: {uec_prices.shape}")
print(f"Date range: {ccj_prices.index[0]} to {ccj_prices.index[-1]}")

# Step 4: Perform the cointegration test (Engle-Granger)
score, p_value, _ = coint(ccj_prices, uec_prices)

# Step 5: Interpret the result
print(f'\nCointegration Test p-value: {p_value:.6f}')
if p_value < 0.05:
    print("The series are cointegrated!")
else:
    print("The series are not cointegrated.")

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

# Step 7: Calculate and plot the spread (difference) between the two series
spread = ccj_prices - uec_prices

# Check for NaN values in the spread
if spread.isna().sum() > 0:
    print(f"Warning: There are {spread.isna().sum()} NaN values in the spread.")
    spread = spread.dropna()

print(f"Spread statistics - Mean: {spread.mean():.2f}, Std: {spread.std():.2f}")

# Plot the spread with proper formatting
plt.figure(figsize=(12, 5))
plt.plot(spread.index, spread.values, label='Spread: CCJ - UEC', color='purple', linewidth=1)
plt.axhline(y=spread.mean(), color='red', linestyle='--', label='Mean', linewidth=1)
plt.axhline(y=spread.mean() + 2*spread.std(), color='orange', linestyle=':', 
            label='+2 Std Dev', linewidth=1)
plt.axhline(y=spread.mean() - 2*spread.std(), color='orange', linestyle=':', 
            label='-2 Std Dev', linewidth=1)
plt.title('Spread: CCJ - UEC (with Mean and ±2 Std Dev)')
plt.xlabel('Date')
plt.ylabel('Price Difference (USD)')
plt.legend(loc='best')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()"""