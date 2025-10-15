# Statistical Arbitrage Model Constants

# Ticker symbols for the asset pair
TICKER_1 = 'CCJ'
TICKER_2 = 'UEC'

# Data date range for backtesting
START_DATE = '2010-01-01'
END_DATE = '2025-01-01'

# Data cache filenames
DATA_FILE_1 = f'{TICKER_1}_data.csv'
DATA_FILE_2 = f'{TICKER_2}_data.csv'

# Analysis parameters
ROLLING_WINDOW_DAYS = 60

# Statistical thresholds
COINTEGRATION_P_THRESHOLD = 0.05
Z_SCORE_ENTRY_THRESHOLD = 0.5
Z_SCORE_EXIT_THRESHOLD = 0.25
EXTREME_STOP = 4

