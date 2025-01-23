# given weights and tickers

from alpaca.trading.client import TradingClient
import pandas as pd
import numpy as np
import load_dotenv
import os


class Trader:
    def __init__(self):
        load_dotenv.load_dotenv()

        self.key = os.getenv("ALPACA_KEY")
        self.secret = os.getenv("ALPACA_SECRET")
        self.trading_client = TradingClient(self.key, self.secret)

    def execute(self, trades):
        '''
        Execute trades for the strategy based on newly updated weights

        Returns:
        - status: True if all trades completed, False otherwise
        '''

        return True
        

    def liquidate(self):
        '''
        Exit all positions
        '''
        self.trading_client.close_all_position(True)



if __name__ == "__main__":
    trader = Trader()
