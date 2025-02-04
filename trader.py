# given weights and tickers

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
import numpy as np
import load_dotenv
import os
import sys


class Trader:
    def __init__(self):
        load_dotenv.load_dotenv()

        self.key = os.getenv("ALPACA_KEY")
        self.secret = os.getenv("ALPACA_SECRET")
        self.trading_client = TradingClient(self.key, self.secret)
        self.account = self.trading_client.get_account()
        self.data_client = StockHistoricalDataClient(self.key, self.secret)

    def trade_procedure(self, trades: pd.DataFrame):
        '''
        Prepares trades for the strategy based on newly updated weights

        Returns:
        - status: True if all trades completed, False otherwise
        '''

        orders = []

        for trade in trades.to_dict(orient="records"):
            order = self.market_order_setup(trade)
            orders.append(order)
        
        if(input("Would you like to proceed with the trade? Y/n") != "Y"):
            exit()

        self.execute(orders=orders)
        print("Orders submitted")
    

    def execute(self, orders: list):
        '''
        Execute trades as determined by trade_prep
        '''

        for order in orders:
            self.trading_client.submit_order(order)


    def market_order_setup(self, trade) -> MarketOrderRequest:
        '''
        Helper method to setup trade object

        Returns:
        - order: the MarketOrder object to be added to the tradelist
        '''

        buying_power = float(self.account.buying_power) # get current AUM
        ticker = trade["symbol"]
        weight = trade["weights"]

        # get latest price of desired stock
        trade_req = StockLatestTradeRequest(symbol_or_symbols=ticker)
        latest_trade = self.data_client.get_stock_latest_trade(trade_req)
        latest_price = latest_trade[ticker].price

        shares = (weight * buying_power) / latest_price # calculate # of shares required for correct sizing

        shares = shares // 1

        trade_size = shares # initialize to 0
        open_positions = self.trading_client.get_all_positions()

        for position in open_positions:
            if position.symbol == ticker:
                trade_size = shares - position.qty

        if trade_size == 0: 
            sys.exit()

        return MarketOrderRequest(
            symbol = ticker,
            qty = abs(trade_size),
            side = OrderSide.SELL if trade_size < 0 else OrderSide.BUY,
            time_in_force = TimeInForce.DAY
        )

    def liquidate(self):
        '''
        Exit all positions
        '''
        self.trading_client.close_all_position(True)

    def cancel_all(self):
        '''
        Cancel all open orders
        '''
        self.trading_client.cancel_orders()

    def read_tickers(self, path) -> pd.DataFrame:
        '''
        Read the tickers from a CSV file

        Returns:
        - df: the dataframe containing the tickers
        '''

        df = pd.read_csv(path)

        return df

if __name__ == "__main__":
    trader = Trader()
    print(trader.account.portfolio_value)
