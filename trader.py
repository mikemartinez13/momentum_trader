# given weights and tickers

import alpaca.common.exceptions
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

        for trade in trades:
            order = self.market_order_setup(trade)
            orders.append(order)
        
        self.execute(orders=orders)
    

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

        port_aum = self.account.portfolio_value # get current AUM
        ticker = trade["symbol"]
        weight = trade["weights"]

        # get latest price of desired stock
        trade_req = StockLatestTradeRequest(symbol_or_symbols=ticker)
        latest_trade = self.data_client.get_stock_latest_trade(trade_req)
        latest_price = latest_trade[ticker].price

        shares = (weight * port_aum) / latest_price # calculate # of shares required for correct sizing


        trade_size = 0 # initialize to 0
        open_positions = self.trading_client.get_all_positions()

        for position in open_positions:
            if position.symbol == ticker:
                trade_size = shares - position.qty

        return MarketOrderRequest(
            symbol = ticker,
            qty = abs(trade_size),
            side = OrderSide.SELL if trade_size < 0 else OrderSide.BUY,
            TimeInForce = TimeInForce.DAY
        )


    def liquidate(self):
        '''
        Exit all positions
        '''
        self.trading_client.close_all_position(True)


if __name__ == "__main__":
    trader = Trader()
