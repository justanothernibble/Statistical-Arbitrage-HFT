import os
import yfinance as yf
import pandas as pd
import statsmodels.api as sm

# Get the directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
stocks = ['CCJ', 'UEC']
data = yf.download(stocks, interval='1wk',period='1y')

# Debug: Print the column structure
print("Columns:", data.columns)
print("\nFirst few rows:")
print(data.head())

# Access the 'Close' price for each stock from the MultiIndex
y = data['Close']['CCJ']
x = sm.add_constant(data['Close']['UEC'])

res = sm.OLS(y, x).fit()
beta = res.params['UEC']

# Calculate spread using Close prices
spread = data['Close']['CCJ'] - beta * data['Close']['UEC']

print(f"\nBeta: {beta}")
print(f"\nSpread:\n{spread}")
