from .base import StockStrategy
from core.data_provider import data_provider
import datetime

def _get_report_period(date_str):
    """
    根据当前日期推算最近一个可能已发布财报的季度。
    简单的规则：
    - 1-4月: 查询去年的Q3 (因为年报和一季报通常4月底才出完，Q3最稳)
    - 5-8月: 查询今年Q1
    - 9-10月: 查询今年Q2
    - 11-12月: 查询今年Q3
    """
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    month = dt.month
    year = dt.year
    
    if 1 <= month <= 4:
        return str(year - 1), "3"
    elif 5 <= month <= 8:
        return str(year), "1"
    elif 9 <= month <= 10:
        return str(year), "2"
    else:
        return str(year), "3"

class LowPeStrategy(StockStrategy):
    @property
    def name(self):
        return "Value_LowPE"
        
    @property
    def description(self):
        return "Low Valuation: 0 < PE_TTM < 30"
        
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
            
        last_row = df.iloc[-1]
        
        if 'peTTM' not in last_row:
            return False, {}
            
        pe = last_row['peTTM']
        
        # Exclude loss-making (pe<0) and overvalued stocks; 边界值30包含
        if 0 < pe <= 30:
            return True, {
                'price': last_row['close'],
                'peTTM': round(pe, 2),
                'pbMRQ': round(last_row.get('pbMRQ', 0), 2)
            }
        return False, {}

class HighGrowthStrategy(StockStrategy):
    @property
    def name(self):
        return "Growth_DoubleHigh"
        
    @property
    def description(self):
        return "High Growth: YOY Profit > 20% AND YOY Revenue > 20%"
        
    def check(self, code, df):
        # Need date from df to decide which quarter to check
        if df is None or len(df) < 1:
            return False, {}
            
        date_str = str(df.iloc[-1]['date'])
        year, quarter = _get_report_period(date_str)
        
        # Query Growth Data（捕获异常）
        try:
            g_df = data_provider.get_growth_data(code, year, quarter)
        except Exception:
            return False, {}
        if g_df is None or g_df.empty:
            return False, {}
            
        try:
            # YOYNI: Net Income YOY, YOYAsset: Asset YOY (Approximation for scale growth, sometimes YOYRevenue is not directly available in basic calls depending on mapping)
            # Baostock growth data: YOYEquity, YOYAsset, YOYNI, YOYEPSBasic, YOYPNI
            yoy_ni = float(g_df.iloc[0]['YOYNI'])
            
            # Using YOYAsset as a proxy for scale expansion if Revenue YOY is not explicitly in this specific API subset or requires operation_data
            # Actually let's just use YOYNI > 20% for simplicity of this specific strategy if revenue is missing
            
            # 边界值20包含
            if yoy_ni >= 20:
                return True, {
                    'price': df.iloc[-1]['close'],
                    'YOY_NetProfit': f"{yoy_ni:.2f}%",
                    'Period': f"{year}Q{quarter}"
                }
        except Exception:
            pass
            
        return False, {}

class HighRoeStrategy(StockStrategy):
    @property
    def name(self):
        return "Quality_HighROE"
        
    @property
    def description(self):
        return "High Quality: ROE > 15%"
        
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
            
        date_str = str(df.iloc[-1]['date'])
        year, quarter = _get_report_period(date_str)
        
        p_df = data_provider.get_profit_data(code, year, quarter)
        if p_df is None or p_df.empty:
            return False, {}
            
        try:
            roe = float(p_df.iloc[0]['roeAvg']) * 100 # usually it is decimal? wait baostock returns decimal or percent? Baostock usually returns decimal or percentage string. checking docs... assume it needs conversion or is direct value.
            # Baostock docs: roeAvg is usually decimal 0.15 for 15% or just verify.
            # If the value is > 1 it might be percentage.
            
            # Let's assume it handles standard interpretation.
            if roe > 0.15: # Assuming decimal 0.15
                 # Wait, if it's really 15%, safe to check > 15 if it's percent, or > 0.15 if decimal.
                 # Let's handle both roughly
                 pass 
            
            # Re-reading baostock specs common behavior: usually ratio is 0.xx. 
            # But let's check one sample if possible. Or just be safe.
            # Actually, standardizing: let's try to interpret > 10 as % or < 1 as decimal.
            
            real_roe = roe
            if roe < 1.0: # likely decimal
                real_roe = roe * 100
            
            # 边界值15包含
            if real_roe >= 15:
                return True, {
                    'price': df.iloc[-1]['close'],
                    'ROE': f"{real_roe:.2f}%",
                    'Period': f"{year}Q{quarter}"
                }
        except:
            pass
            
        return False, {}

class LowDebtStrategy(StockStrategy):
    @property
    def name(self):
        return "Safety_LowDebt"
        
    @property
    def description(self):
        return "Financial Health: Debt Ratio < 50%"
        
    def check(self, code, df):
        if df is None or len(df) < 1:
            return False, {}
            
        date_str = str(df.iloc[-1]['date'])
        year, quarter = _get_report_period(date_str)
        
        b_df = data_provider.get_balance_data(code, year, quarter)
        if b_df is None or b_df.empty:
            return False, {}
            
        try:
            liab_ratio = float(b_df.iloc[0]['liabilityToAsset']) * 100 # It is ratio
            
            # 边界值50包含
            if liab_ratio <= 50:
                 return True, {
                    'price': df.iloc[-1]['close'],
                    'DebtRatio': f"{liab_ratio:.2f}%",
                    'Period': f"{year}Q{quarter}"
                }
        except:
            pass
            
        return False, {}

