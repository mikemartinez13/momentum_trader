from tradingview_screener import Query, col
from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from datetime import datetime, timedelta, tzinfo, timezone  
from alpaca.data.timeframe import TimeFrame
import load_dotenv
import os
import numpy as np


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
        for company in companies_ath: 
            cur_data = bars.xs(company, level=0)
            avg_dollar_vol = (cur_data['close'].dot(cur_data['volume']))/len(cur_data)
            last_close = cur_data['close'].iloc[-1]
            if avg_dollar_vol >= 1e6 and last_close >= 10: # filter logic per page 4 of the paper
                qualifying_companies.append(company)

        # Return only the qualifying companies
        return qualifying_companies, bars.loc[qualifying_companies]

if __name__ == "__main__":
    screener = MomentumScreener()

    tickers, _ = screener.screen()

    print(tickers)

