# given weights and tickers

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
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

    def trade_prep(self, trades: pd.DataFrame) -> bool:
        '''
        Prepares trades for the strategy based on newly updated weights

        Returns:
        - status: True if all trades completed, False otherwise
        '''

# column called symbol and column called weights

        for trade in trades:
            order = self.market_order_setup(trade)
            
        return True
        

    def market_order_setup(self, trade) -> MarketOrderRequest:
        '''
        Helper method to setup trade object

        Returns:
        - order: the MarketOrder object to be added to the tradelist
        '''

        ticker = trade["symbol"]
        weight = trade["weights"]

        shares = 1 # multiply weight by portfolio AUM, divide by last share price

        trade_size = 1 # get current position and subtract new position

    def exit_positions(self):
        '''
        Exits positions when determined by exit strategy
        '''

    def liquidate(self):
        '''
        Exit all positions
        '''
        self.trading_client.close_all_position(True)



if __name__ == "__main__":
    trader = Trader()
