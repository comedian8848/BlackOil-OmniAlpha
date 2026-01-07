import baostock as bs
import pandas as pd
import datetime

class BaostockProvider:
    def __init__(self):
        self.is_logged_in = False

    def login(self):
        if not self.is_logged_in:
            bs.login()
            self.is_logged_in = True

    def logout(self):
        if self.is_logged_in:
            bs.logout()
            self.is_logged_in = False

    def get_latest_trading_date(self):
        self.login()
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        start_lookback = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        rs = bs.query_trade_dates(start_date=start_lookback, end_date=today)
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
            
        if not data_list: return today
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        trading_days = df[df['is_trading_day'] == '1']['calendar_date'].tolist()
        return trading_days[-1] if trading_days else today

    def get_hs300_stocks(self, date):
        self.login()
        print(f"正在获取 {date} 的沪深300成分股...")
        rs = bs.query_hs300_stocks(date=date)
        hs300_stocks = []
        while (rs.error_code == '0') & rs.next():
            hs300_stocks.append(rs.get_row_data()[1]) # code is at index 1
        return hs300_stocks

    def get_daily_bars(self, code, end_date, lookback_days=60):
        self.login()
        start_date = (datetime.datetime.strptime(end_date, "%Y-%m-%d") - datetime.timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        # Increased fields to support more strategies (peTTM, pbMRQ, turn, isST)
        rs = bs.query_history_k_data_plus(code,
            "date,code,open,high,low,close,volume,amount,pctChg,peTTM,pbMRQ,turn,isST",
            start_date=start_date, end_date=end_date,
            frequency="d", adjustflag="3")
        
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
            
        if not data_list:
            return None

        df = pd.DataFrame(data_list, columns=rs.fields)
        
        # Data Type Conversion
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'pctChg', 'peTTM', 'pbMRQ', 'turn']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
        return df

# Singleton instance for easy access
data_provider = BaostockProvider()
