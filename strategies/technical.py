from .base import StockStrategy

class MovingAverageStrategy(StockStrategy):
    @property
    def name(self):
        return "MA_Trend"

    @property
    def description(self):
        return "Moving Average Trend: Close > MA20 & MA5 > MA20"

    def check(self, code, df):
        if df is None or len(df) < 20:
            return False, {}
            
        df = df.copy() # Avoid SettingWithCopyWarning
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        
        last_row = df.iloc[-1]
        
        condition_1 = last_row['close'] > last_row['MA20']
        condition_2 = last_row['MA5'] > last_row['MA20']
        # 进一步筛选：最近5天收盘价单调上升，避免噪声数据误匹配
        recent_diff = df['close'].diff().tail(5)
        strong_uptrend = (recent_diff > 0).all()
        
        if condition_1 and condition_2 and strong_uptrend:
            return True, {
                'price': last_row['close'],
                'MA5': round(last_row['MA5'], 2),
                'MA20': round(last_row['MA20'], 2)
            }
        return False, {}

class VolumeRiseStrategy(StockStrategy):
    @property
    def name(self):
        return "Volume_Breakout"

    @property
    def description(self):
        return "Volume Breakout: Rise > 2% & Volume > 1.5 * MA_VOL5"

    def check(self, code, df):
        if df is None or len(df) < 6:
            return False, {}
        
        df = df.copy()
        df['MA_VOL5'] = df['volume'].rolling(window=5).mean()
        
        last_row = df.iloc[-1]
        
        is_up = last_row['pctChg'] > 2.0
        is_volume_up = last_row['volume'] > (last_row['MA_VOL5'] * 1.5)
        
        if is_up and is_volume_up:
            return True, {
                'price': last_row['close'],
                'pctChg': last_row['pctChg'],
                'vol_ratio': round(last_row['volume'] / last_row['MA_VOL5'], 2)
            }
        return False, {}

class HighTurnoverStrategy(StockStrategy):
    @property
    def name(self):
        return "High_Turnover"
        
    @property
    def description(self):
        return "High Turnover: Turnover > 5% & Not ST"
        
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
            
        last_row = df.iloc[-1]
        turn = last_row.get('turn', 0)
        is_st = last_row.get('isST', '0') # '1' is ST
        
        if turn >= 5 and str(is_st) != '1':
            return True, {
                'price': last_row['close'],
                'turn': round(turn, 2),
                'pctChg': round(last_row.get('pctChg', 0), 2)
            }
        return False, {}
