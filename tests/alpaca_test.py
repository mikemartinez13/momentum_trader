# from alpaca.trading.client import TradingClient
# from alpaca.trading.requests import MarketOrderRequest
# from alpaca.trading.enums import OrderSide, TimeInForce

# trading_client = TradingClient("PK9NYJ8P32UGMTAAWZI9", "mKgz5zT8aR0pD7efXreYsrW3EbAv59BdjRjFmLX9")

# market_order_data = MarketOrderRequest(
#     symbol='SPY',
#     qty=1,
#     side=OrderSide.BUY,
#     time_in_force=TimeInForce.DAY # How long the order will be active
# )

# market_order = trading_client.submit_order(market_order_data)
# print(market_order)

# limit_order_data = MarketOrderRequest(
#     symbol='SPY',
#     qty=1,
#     side=OrderSide.BUY,
#     time_in_force=TimeInForce.DAY,
#     limit_price=486.00
# )

# limit_order = trading_client.submit_order(limit_order_data)
# Limit order allows you to specify the price you want to buy or sell at

# print(trading_client.get_account().account_number)
# print(trading_client.get_account().buying_power)

from alpaca.data import StockHistoricalDataClient, StockTradesRequest, StockBarsRequest
from datetime import datetime, timedelta, tzinfo, timezone  
from zoneinfo import ZoneInfo
from alpaca.data.timeframe import TimeFrame

data_client = StockHistoricalDataClient("PK9NYJ8P32UGMTAAWZI9", "mKgz5zT8aR0pD7efXreYsrW3EbAv59BdjRjFmLX9")

# request_params = StockTradesRequest(
#     symbol_or_symbols="AAPL",
#     start=datetime(2024, 1, 30, 14, 30), # 9:30 AM in UTC time
#     end=datetime(2024, 1, 30, 14, 45),
# )
market_start = datetime.now() - timedelta(days=42)
market_start = market_start.replace(hour=9, 
                                    minute=30, 
                                    second=0, 
                                    microsecond=0, 
                                    tzinfo=timezone.utc)
market_end = datetime.now()

request_params = StockBarsRequest(
    symbol_or_symbols="AAPL",
    start=market_start, # 9:30 AM in UTC time
    end=market_end,
    timeframe=TimeFrame.Day
)

# trades = data_client.get_stock_trades(request_params)
bars = data_client.get_stock_bars(request_params)

print(bars)


# from alpaca.data.historical import CryptoHistoricalDataClient
# from alpaca.data.requests import CryptoBarsRequest
# from alpaca.data.timeframe import TimeFrame
# from datetime import datetime

# # no keys required for crypto data
# client = CryptoHistoricalDataClient()

# request_params = CryptoBarsRequest(
#                         symbol_or_symbols=["BTC/USD", "ETH/USD"],
#                         timeframe=TimeFrame.Day,
#                         start=datetime(2022, 7, 1),
#                         end=datetime(2022, 9, 1)
#                  )

# bars = client.get_crypto_bars(request_params)

# # convert to dataframe
# bars.df

# # access bars as list - important to note that you must access by symbol key
# # even for a single symbol request - models are agnostic to number of symbols
# print(bars["BTC/USD"])


# from alpaca.data.live import StockDataStream

# stream = StockDataStream("PK9NYJ8P32UGMTAAWZI9", "mKgz5zT8aR0pD7efXreYsrW3EbAv59BdjRjFmLX9")

# async def handle_quote(data):
#     print(data)

# stream.subscribe_quotes(handle_quote, 'AAPL')

# stream.run()

