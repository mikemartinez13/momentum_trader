from screener import MomentumScreener
from trader import Trader
import pandas as pd
import numpy as np

if __name__ == "__main__":
    mscreener = MomentumScreener()

    tickers, df = mscreener.screen()
    newdf = mscreener.update_weights(df)
    print(newdf)

    trader = Trader()
    trader.trade_procedure(newdf)
