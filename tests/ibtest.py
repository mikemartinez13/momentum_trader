from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from ibapi.contract import Contract # Symbol and exchange
from ibapi.order import Order # For submitting orders
import threading # For multithreading
import time

import sys

# Vars

# Class for Interactive Brokers Connection
class IBApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    # Listen for realtime bars
    def realtimeBar(self, reqId, time, open_, high, low, close, volume, wap, count):
        super().realtimeBar(reqId, time, open_, high, low, close, volume, wap, count)
        try:
            bot.on_bar_update(reqId, time, open_, high, low, close, volume, wap, count)
        except Exception as e:
            print(e)
            bot.close()
    
    def error(self, reqId, errorCode, errorString):
        print(errorCode)
        print(errorString)

# Bot logic
class Bot:
    ib = None
    def __init__(self):
        # Connect to IB on init
        self.ib = IBApi()
        self.ib.connect('127.0.0.1',7496,1)
        ib_thread = threading.Thread(target=self.run_loop, daemon=True) # allows us to separate threads. 
        ib_thread.start()
            # Daemon=True allows the program to exit even if the thread is still running
        # Separate the run method to a separate thread
        # this will prevent the next line from running until the connection is closed

        time.sleep(1)
        symbol = input("Enter the symbol you want to trade :")

        self.ib.reqMarketDataType(3) 
        
        # Create our contract object
        contract = Contract() # need to create a contract to trade
        contract.symbol = symbol.upper()
        contract.secType = 'STK' # Security type
        contract.exchange = 'SMART' # auto-select exchange
        contract.currency = 'USD'

        # Request realtime data
        self.ib.reqRealTimeBars(0, contract, 5, 'TRADES', True, []) # can either get trades, midpoints, bid, ask.

    # Listen to socket in separate thread
    def run_loop(self):
        try:
            self.ib.run()
        except Exception as e:
            print("Exception in run loop :", e)
            self.close()

    def on_bar_update(self, reqId, time, open_, high, low, close, volume, wap, count):
        print(reqId)

    def close(self):
        print("Closing IB connection and exiting...")
        self.ib.disconnect()
        sys.exit(0)

    
# Start the bot
if __name__ == '__main__':
    bot = Bot()

# Next, start coding the strategy. Get data from IKBR. 