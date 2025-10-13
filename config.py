def importLibs(tested):
    if tested == True:
        # import backtesting
        return
    else:
        import yfinance as yf
        import numpy as np
        import pandas as pd
        import statsmodels.api as sm
        from statsmodels.tsa.stattools import coint
        import matplotlib.pyplot as plt
        # import backtesting
        return