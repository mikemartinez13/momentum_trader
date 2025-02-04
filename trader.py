# given weights and tickers

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
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


    def determine_exit(self, ticker, ath):
        '''
        Determine whether to close a position based on the exit criteria

        Returns:
        - 0 if position should be closed (or not traded i.e. not enough data)
        - 1 if position should be help
        '''

    def calculateATR(self, ticker):
        '''
        For a given ticker, calculate the ATR.

        Returns:
        - 0 if there is not enough data to calculate the ATR
        - the ATR value if it can be calculated
        '''

        # 42 days of true ranges to build the ATR 
        # if there aren't 42 days of data, then return 0
        # multiply whatever weight is currently set times 0 if above or ATR condition met, else multiply by 1 

        if ticker: # if we are calculating ATR for the first time - need to check if ATR is stored in the frame
            true_ranges = []
            # For each day in the 42-day range
            for i in range(42):
                days_ago = datetime.date.today() - datetime.timedelta(days=i)
                days_ago_before = days_ago - datetime.timedelta(days=1)

                request_params_day_of = StockBarsRequest( # get data for day of
                    symbol_or_symbols=ticker,
                    timeframe=TimeFrame.DAY,
                    start=days_ago,
                    end=days_ago
                )

                request_params_day_before = StockBarsRequest( # get data for day before
                    symbol_or_symbols=ticker,
                    timeframe=TimeFrame.DAY,
                    start=days_ago_before,
                    end=days_ago_before
                )

                # If data for this ticker does not exist days_ago
                try:
                    prev_bars = self.data_client.get_stock_bars(request_params_day_of).df
                    bars = self.data_client.get_stock_bars(request_params_day_of).df
                except:
                    return 0
                
                # calculate the three TR components
                t1 = bars['high'] - bars['low']
                t2 = abs(bars['high'] - prev_bars['close'])
                t3 = abs(prev_bars['close'] - bars['low'])
                t = [t1, t2, t3]    
                true_ranges.append(max(t)) 
            
            atr = np.mean(true_ranges) # calculate ATR
            return atr
        
        else:
            # get atr from database, multiply by 41, add todays true range, divide by 42
            old_atr = 0 # get from database
            
            today = datetime.date.today()
            yesterday = datetime.date.today() - datetime.timedelta(days=1)

            request_params_day_of = StockBarsRequest( # get data for day of
                    symbol_or_symbols=ticker,
                    timeframe=TimeFrame.DAY,
                    start=today,
                    end=today
                )

            request_params_day_before = StockBarsRequest( # get data for day before
                symbol_or_symbols=ticker,
                timeframe=TimeFrame.DAY,
                start=yesterday,
                end=yesterday
            )
            
            # check if data exists in alpaca
            try:
                prev_bars = self.data_client.get_stock_bars(request_params_day_of).df
                bars = self.data_client.get_stock_bars(request_params_day_of).df
            except:
                return 0
            
            # calculate the three TR components
            t1 = bars['high'] - bars['low']
            t2 = abs(bars['high'] - prev_bars['close'])
            t3 = abs(prev_bars['close'] - bars['low'])
            t = [t1, t2, t3] 

            atr = (41 * old_atr + max(t)) / 42
            return atr


        

    # Helper functions

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
