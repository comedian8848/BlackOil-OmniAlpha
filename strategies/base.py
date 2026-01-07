from abc import ABC, abstractmethod

class StockStrategy(ABC):
    """
    Abstract base class for all stock selection strategies.
    """
    
    @property
    @abstractmethod
    def name(self):
        """Strategy Name"""
        pass

    @property
    @abstractmethod
    def description(self):
        """Strategy Description"""
        pass

    @abstractmethod
    def check(self, code, data_df):
        """
        Check if a stock meets the strategy criteria.
        
        :param code: Stock code
        :param data_df: Historical data DataFrame (including date, close, volume, etc.)
        :return: (bool, dict) -> (Is Selected, Details/Reason)
        """
        pass
