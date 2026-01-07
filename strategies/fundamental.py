from .base import StockStrategy

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
        
        # Exclude loss-making (pe<0) and overvalued stocks
        if 0 < pe < 30:
            return True, {
                'price': last_row['close'],
                'peTTM': round(pe, 2),
                'pbMRQ': round(last_row.get('pbMRQ', 0), 2)
            }
        return False, {}
