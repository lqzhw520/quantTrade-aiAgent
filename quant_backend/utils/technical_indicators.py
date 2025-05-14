import pandas as pd
import numpy as np
from typing import Tuple, Optional

class TechnicalIndicators:
    """技术指标计算工具类"""
    
    @staticmethod
    def calculate_ma(data: pd.Series, window: int) -> pd.Series:
        """
        计算移动平均线 (Moving Average)
        
        Args:
            data: 价格数据序列
            window: 移动窗口大小
            
        Returns:
            移动平均线序列
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, window: int) -> pd.Series:
        """
        计算指数移动平均线 (Exponential Moving Average)
        
        Args:
            data: 价格数据序列
            window: 移动窗口大小
            
        Returns:
            指数移动平均线序列
        """
        return data.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.Series, window: int = 14) -> pd.Series:
        """
        计算相对强弱指标 (Relative Strength Index)
        
        Args:
            data: 价格数据序列
            window: RSI 计算窗口大小，默认14天
            
        Returns:
            RSI 指标序列
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.Series, 
                      fast_period: int = 12, 
                      slow_period: int = 26, 
                      signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算 MACD 指标 (Moving Average Convergence Divergence)
        
        Args:
            data: 价格数据序列
            fast_period: 快线周期，默认12
            slow_period: 慢线周期，默认26
            signal_period: 信号线周期，默认9
            
        Returns:
            (MACD线, 信号线, MACD柱状图)
        """
        exp1 = data.ewm(span=fast_period, adjust=False).mean()
        exp2 = data.ewm(span=slow_period, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, 
                                window: int = 20, 
                                num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算布林带 (Bollinger Bands)
        
        Args:
            data: 价格数据序列
            window: 移动窗口大小，默认20天
            num_std: 标准差倍数，默认2.0
            
        Returns:
            (中轨, 上轨, 下轨)
        """
        middle_band = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        upper_band = middle_band + (std * num_std)
        lower_band = middle_band - (std * num_std)
        return middle_band, upper_band, lower_band
    
    @staticmethod
    def calculate_atr(high: pd.Series, 
                     low: pd.Series, 
                     close: pd.Series, 
                     window: int = 14) -> pd.Series:
        """
        计算平均真实波幅 (Average True Range)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            window: ATR 计算窗口大小，默认14天
            
        Returns:
            ATR 指标序列
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        return atr
    
    @staticmethod
    def calculate_stochastic(high: pd.Series, 
                           low: pd.Series, 
                           close: pd.Series, 
                           k_window: int = 14, 
                           d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        计算随机指标 (Stochastic Oscillator)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            k_window: %K 计算窗口大小，默认14天
            d_window: %D 计算窗口大小，默认3天
            
        Returns:
            (%K线, %D线)
        """
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_window).mean()
        # 将超出范围的值限制在0-100之间
        k = k.clip(0, 100)
        d = d.clip(0, 100)
        return k, d
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        计算能量潮指标 (On-Balance Volume)
        
        Args:
            close: 收盘价序列
            volume: 成交量序列
            
        Returns:
            OBV 指标序列
        """
        price_change = close.diff()
        obv = pd.Series(0, index=close.index)
        obv[price_change > 0] = volume[price_change > 0]
        obv[price_change < 0] = -volume[price_change < 0]
        return obv.cumsum()
    
    @staticmethod
    def calculate_ichimoku(high: pd.Series, 
                          low: pd.Series, 
                          conversion_period: int = 9, 
                          base_period: int = 26, 
                          span_b_period: int = 52, 
                          displacement: int = 26) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        计算一目均衡图 (Ichimoku Cloud)
        
        Args:
            high: 最高价序列
            low: 最低价序列
            conversion_period: 转换线周期，默认9
            base_period: 基准线周期，默认26
            span_b_period: 先行带B周期，默认52
            displacement: 延迟线位移，默认26
            
        Returns:
            (转换线, 基准线, 先行带A, 先行带B, 延迟线)
        """
        # 转换线 (Conversion Line)
        conversion_line = (high.rolling(window=conversion_period).max() + 
                         low.rolling(window=conversion_period).min()) / 2
        
        # 基准线 (Base Line)
        base_line = (high.rolling(window=base_period).max() + 
                    low.rolling(window=base_period).min()) / 2
        
        # 先行带A (Leading Span A)
        leading_span_a = ((conversion_line + base_line) / 2).shift(displacement)
        
        # 先行带B (Leading Span B)
        leading_span_b = ((high.rolling(window=span_b_period).max() + 
                          low.rolling(window=span_b_period).min()) / 2).shift(displacement)
        
        # 延迟线 (Lagging Span)
        lagging_span = low.shift(-displacement)
        
        return conversion_line, base_line, leading_span_a, leading_span_b, lagging_span 