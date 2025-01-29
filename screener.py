from tradingview_screener import Query, col
from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from datetime import datetime, timedelta, tzinfo, timezone  
from alpaca.data.timeframe import TimeFrame

import load_dotenv
import os
import numpy as np
import pandas as pd


class MomentumScreener:
    def __init__(self):
        load_dotenv.load_dotenv()

        self.key = os.getenv("ALPACA_KEY")
        self.secret = os.getenv("ALPACA_SECRET")

    def query_stocks(self):
        '''
        Use TradingView screener to find stocks that are at all time highs.

        Returns:
        - companies: list of companies that are at all time highs.
        - df_ath: dataframe of companies that are at all time highs with relevant info.
        '''
        df_ath = (Query()
        .select(
            'name',
            'description',
            'close',
            'pricescale',
            'minmov',
            'fractional',
            'minmove2',
            'currency',
            'change',
            'volume',
            'market',
            'recommendation_mark',
            'relative_volume_10d_calc',
        )
        .where(
            col('exchange').isin(['AMEX', 'CBOE', 'NASDAQ', 'NYSE']),
            col('is_primary') == True,
            col('typespecs').has('common'),
            col('typespecs').has_none_of('preferred'),
            col('type') == 'stock',
            col('High.All') <= 'high',
            col('active_symbol') == True,
        )
        .order_by('name', ascending=True, nulls_first=False)
        .limit(1000)
        .set_markets('america')
        .set_property('preset', 'all_time_high')
        .set_property('symbols', {'query': {'types': ['stock', 'fund', 'dr', 'structured']}})
        .get_scanner_data())[1]

        companies = df_ath['name'].to_list()

        return companies, df_ath

    def screen(self) -> list:
        '''
        Use Alpaca historical data to screen out companies that have an average dollar volume of less than 1 million
        per the methodology of [the momentum trading paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5084316).
        '''
        companies_ath, df_ath = self.query_stocks()

        data_client = StockHistoricalDataClient(self.key, self.secret)

        market_start = datetime.now() - timedelta(days=42)
        market_start = market_start.replace(hour=9, 
                                            minute=30, 
                                            second=0, 
                                            microsecond=0, 
                                            tzinfo=timezone.utc)
        market_end = datetime.now()

        request_params = StockBarsRequest(
            symbol_or_symbols=companies_ath,
            start=market_start, # 9:30 AM in UTC time
            end=market_end,
            timeframe=TimeFrame.Day
        )

        bars = data_client.get_stock_bars(request_params).df

        qualifying_companies = []
        volatilities = [] # store the 42-day volatilities of the companies

        for company in companies_ath: 
            cur_data = bars.xs(company, level=0)
            if len(cur_data) == 1:
                continue # if there is only one data point, we cannot calculate the average dollar volume or volatility
            avg_dollar_vol = (cur_data['close'].dot(cur_data['volume']))/len(cur_data)
            last_close = cur_data['close'].iloc[-1]
            if avg_dollar_vol >= 1e6 and last_close >= 10: # filter logic per page 4 of the paper
                qualifying_companies.append(company)

                # Calculate the 42-day volatility

                returns = np.log(cur_data['close']/cur_data['close'].shift(1))
                daily_std = returns.std()
                volatilities.append(daily_std*np.sqrt(42)) # annualized to 42 days (page 18)
                # if company == 'SFD': # this stock just IPOed, so there are no returns to compare against. It is also very illiquid. 
                #     print('Cur data:', cur_data)
                #     print('\nReturns:', returns)
                #     print(daily_std)
                #     print(daily_std*np.sqrt(42))

        filtered_bars = bars.loc[qualifying_companies]
        last_close_df = filtered_bars.groupby('symbol').last()
        last_close_df['volatility'] = volatilities

        # Return only the qualifying companies
        return qualifying_companies, last_close_df.reset_index()
    
def update_weights(new_companies_df: pd.DataFrame) -> pd.DataFrame:
    '''
    Update the screener with the latest data and update portfolio weights.
    '''
    df1 = pd.read_csv('tickers') if os.path.exists('tickers') else pd.DataFrame() # read the existing screener data
    if os.path.exists('tickers'):
        df1.update(new_companies_df)
    else:
        df1 = new_companies_df
    
    df1['weights'] = (0.3/df1['volatility']) * (1/max(200, len(df1))) # calculate the weights (page 19) 

    df1['weights'] = df1['weights'] * max(1, 2/df1['weights'].sum()) # scale the weights to account for leverage (page 19)
    
    df1['weights'] = df1['weights'] / df1['weights'].sum() # normalize to 1 for Alpaca trading. 

    df1.to_csv('tickers.csv', index=False) # save the updated screener data

    return df1

# Workflow:
# 1. Run the screener to get the list of companies that are at all time highs.
# 2. Update the weights of the companies in the screener.
# 3. Run exit strategy to sell the companies that are need to be exited
# 4. Run trading bot to buy the companies that are in the screener and sell the companies that are in the exit strategy.


if __name__ == "__main__":
    screener = MomentumScreener()

    tickers, df = screener.screen()

    newdf = update_weights(df)
    print(newdf)
    print(sum(newdf['weights']))

    print(newdf.loc[newdf['weights'].isna()])
