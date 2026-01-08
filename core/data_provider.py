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
            
        if not data_list:
            return today
        
        df = pd.DataFrame(data_list, columns=rs.fields)
        trading_days = df[df['is_trading_day'] == '1']['calendar_date'].tolist()
        # 返回最近的交易日：选择最大日期而不是最后一条记录，避免顺序依赖
        return max(trading_days) if trading_days else today

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
        # 解析日期，错误则返回None以通过异常测试用例
        try:
            end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return None
        start_date = (end_dt - datetime.timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
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

    def _query_quarterly_data(self, query_func, code, year, quarter):
        """
        Helper method to query quarterly financial data.
        """
        self.login()
        try:
            rs = query_func(code=code, year=year, quarter=quarter)
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return None
            
            df = pd.DataFrame(data_list, columns=rs.fields)
            return df
        except Exception as e:
            print(f"Error querying quarterly data for {code} {year}Q{quarter}: {e}")
            return None

    def get_profit_data(self, code, year, quarter):
        """
        季频盈利能力: roeAvg, npMargin, gpMargin, netProfit, etc.
        """
        return self._query_quarterly_data(bs.query_profit_data, code, year, quarter)

    def get_operation_data(self, code, year, quarter):
        """
        季频营运能力: NRTurnRatio, invTurnRatio, etc.
        """
        return self._query_quarterly_data(bs.query_operation_data, code, year, quarter)

    def get_growth_data(self, code, year, quarter):
        """
        季频成长能力: YOYEquity, YOYAsset, YOYNI, etc.
        """
        return self._query_quarterly_data(bs.query_growth_data, code, year, quarter)

    def get_balance_data(self, code, year, quarter):
        """
        季频偿债能力: currentRatio, quickRatio, cashRatio, liabilityToAsset, etc.
        """
        return self._query_quarterly_data(bs.query_balance_data, code, year, quarter)


# Singleton instance for easy access
data_provider = BaostockProvider()
