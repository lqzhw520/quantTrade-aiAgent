import pandas as pd
import numpy as np

class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def calculate_ma(data: pd.Series, window: int) -> pd.Series:
        """
        计算移动平均线
        
        Args:
            data: 价格数据
            window: 窗口大小
            
        Returns:
            Series: 移动平均线数据
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, window: int) -> pd.Series:
        """
        计算指数移动平均线
        
        Args:
            data: 价格数据
            window: 窗口大小
            
        Returns:
            Series: 指数移动平均线数据
        """
        return data.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """
        计算相对强弱指标(RSI)
        
        Args:
            data: 价格数据
            window: 窗口大小
            
        Returns:
            Series: RSI数据
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_macd(data: pd.Series, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> tuple:
        """
        计算MACD指标
        
        Args:
            data: 价格数据
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
            
        Returns:
            tuple: (MACD线, 信号线, 柱状图)
        """
        # 计算快线和慢线的EMA
        ema_fast = data.ewm(span=fast_period, adjust=False).mean()
        ema_slow = data.ewm(span=slow_period, adjust=False).mean()
        
        # 计算MACD线
        macd_line = ema_fast - ema_slow
        
        # 计算信号线
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, 
                                window: int = 20, 
                                num_std: float = 2.0) -> tuple:
        """
        计算布林带
        
        Args:
            data: 价格数据
            window: 窗口大小
            num_std: 标准差倍数
            
        Returns:
            tuple: (中轨, 上轨, 下轨)
        """
        # 计算中轨（移动平均线）
        middle_band = data.rolling(window=window).mean()
        
        # 计算标准差
        std = data.rolling(window=window).std()
        
        # 计算上轨和下轨
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        
        return middle_band, upper_band, lower_band 