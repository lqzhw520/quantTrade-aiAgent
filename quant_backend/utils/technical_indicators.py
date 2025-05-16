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
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """
        计算能量潮指标 (On-Balance Volume, OBV)
        OBV 是根据收盘价涨跌决定成交量的加减累计值，用于衡量资金流向。
        算法：
            - 若本日收盘价 > 前一日收盘价，则 OBV = 前一日 OBV + 本日成交量
            - 若本日收盘价 < 前一日收盘价，则 OBV = 前一日 OBV - 本日成交量
            - 若本日收盘价 = 前一日收盘价，则 OBV = 前一日 OBV
            - 首日 OBV 设为 0
        参数:
            df: 必须包含 'close' 和 'volume' 列的 DataFrame
        返回:
            pd.Series，OBV 序列，索引与输入 df 保持一致
        异常:
            - 若 df 为空或缺少必要列，返回全 0 序列并记录警告日志
        """
        if df is None or df.empty:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 为空，OBV 返回全 0 序列。')
            return pd.Series(0, index=[])
        if not set(['close', 'volume']).issubset(df.columns):
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 缺少 close 或 volume 列，OBV 返回全 0 序列。')
            return pd.Series(0, index=df.index)
        close = df['close']
        volume = df['volume']
        obv = [0]
        for i in range(1, len(df)):
            if pd.isna(close.iloc[i]) or pd.isna(close.iloc[i-1]) or pd.isna(volume.iloc[i]):
                obv.append(obv[-1])
            elif close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=df.index)
    
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
    
    @staticmethod
    def calculate_vma(df: pd.DataFrame, window: int = 5) -> pd.Series:
        """
        计算成交量移动平均线（Volume Moving Average, VMA）
        VMA 用于平滑成交量数据，反映一段时间内的平均成交量水平。
        算法：
            - VMA = 当前及前 (window-1) 日成交量的算术平均值
        参数：
            df: 必须包含 'volume' 列的 DataFrame
            window: 移动平均窗口大小，默认为5
        返回：
            pd.Series，VMA 序列，索引与输入 df 保持一致
        异常：
            - 若 df 为空或缺少 volume 列，返回全 NaN 序列并记录警告日志
        """
        if df is None or df.empty:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 为空，VMA 返回全 NaN 序列。')
            return pd.Series([float('nan')] * 0)
        if 'volume' not in df.columns:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 缺少 volume 列，VMA 返回全 NaN 序列。')
            return pd.Series([float('nan')] * len(df), index=df.index)
        return df['volume'].rolling(window=window, min_periods=1).mean()
    
    @staticmethod
    def calculate_vr(df: pd.DataFrame, window: int = 5) -> pd.Series:
        """
        计算量比（Volume Ratio, VR）
        VR = 当日成交量 / 前N日成交量均值，反映当前成交量相对历史均值的放大或缩小。
        算法：
            - VR = volume / volume.rolling(window=N).mean().shift(1)
            - 首 window 日VR为NaN
        参数：
            df: 必须包含 'volume' 列的 DataFrame
            window: 均值窗口大小，默认为5
        返回：
            pd.Series，VR序列，索引与输入df一致
        异常：
            - 若df为空或缺volume列，返回全NaN序列并记录警告日志
        """
        if df is None or df.empty:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 为空，VR 返回全 NaN 序列。')
            return pd.Series([float('nan')] * 0)
        if 'volume' not in df.columns:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 缺少 volume 列，VR 返回全 NaN 序列。')
            return pd.Series([float('nan')] * len(df), index=df.index)
        avg_vol = df['volume'].rolling(window=window).mean().shift(1)
        vr = df['volume'] / avg_vol
        return vr 
    
    @staticmethod
    def calculate_mfi(df: pd.DataFrame, window: int = 14) -> pd.Series:
        """
        计算资金流量指标（Money Flow Index, MFI）
        MFI 结合价格和成交量，衡量资金流入流出强度，常用于超买超卖判断。
        算法：
            1. 计算典型价格 TP = (high + low + close) / 3
            2. 计算原始资金流 MF = TP * volume
            3. 区分正向资金流和负向资金流（TP较前一日上涨为正，否则为负）
            4. 计算N日正/负向资金流之和，得资金流比率 MR = 正向/负向
            5. MFI = 100 - 100 / (1 + MR)
        参数：
            df: 必须包含 high、low、close、volume 列的 DataFrame
            window: 计算窗口，默认14
        返回：
            pd.Series，MFI序列，索引与输入df一致
        异常：
            - 若df为空或缺必要列，返回全NaN序列并记录警告日志
        """
        required_cols = {'high', 'low', 'close', 'volume'}
        if df is None or df.empty:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 为空，MFI 返回全 NaN 序列。')
            return pd.Series([float('nan')] * 0)
        if not required_cols.issubset(df.columns):
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 缺少 high/low/close/volume 列，MFI 返回全 NaN 序列。')
            return pd.Series([float('nan')] * len(df), index=df.index)
        tp = (df['high'] + df['low'] + df['close']) / 3
        mf = tp * df['volume']
        # 正负资金流
        tp_diff = tp.diff()
        pos_mf = mf.where(tp_diff > 0, 0)
        neg_mf = mf.where(tp_diff < 0, 0).abs()
        pos_sum = pos_mf.rolling(window=window, min_periods=window).sum()
        neg_sum = neg_mf.rolling(window=window, min_periods=window).sum()
        mr = pos_sum / neg_sum
        mfi = 100 - 100 / (1 + mr)
        return mfi 
    
    @staticmethod
    def calculate_pma(df: pd.DataFrame, window: int = 5) -> pd.Series:
        """
        计算价格移动平均线（Price Moving Average, PMA/SMA）
        PMA/SMA 用于平滑价格数据，反映一段时间内的平均收盘价。
        算法：
            - PMA = 当前及前 (window-1) 日收盘价的算术平均值
        参数：
            df: 必须包含 'close' 列的 DataFrame
            window: 移动平均窗口大小，默认为5
        返回：
            pd.Series，PMA 序列，索引与输入 df 保持一致
        异常：
            - 若 df 为空或缺少 close 列，返回全 NaN 序列并记录警告日志
        """
        if df is None or df.empty:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 为空，PMA 返回全 NaN 序列。')
            return pd.Series([float('nan')] * 0)
        if 'close' not in df.columns:
            import logging
            logging.getLogger(__name__).warning('输入 DataFrame 缺少 close 列，PMA 返回全 NaN 序列。')
            return pd.Series([float('nan')] * len(df), index=df.index)
        return df['close'].rolling(window=window, min_periods=1).mean() 