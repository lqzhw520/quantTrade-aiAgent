import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.technical_indicators import TechnicalIndicators

class TestTechnicalIndicators(unittest.TestCase):
    """技术指标计算工具类测试"""
    
    def setUp(self):
        """测试数据准备"""
        # 创建测试用的时间序列
        self.dates = pd.date_range(start='2024-01-01', end='2024-04-10', freq='D')  # 100天
        
        # 创建测试用的价格数据
        np.random.seed(42)
        self.prices = pd.Series(
            np.random.normal(100, 5, len(self.dates)),
            index=self.dates
        )
        
        # 创建测试用的OHLCV数据
        self.high = self.prices + np.random.uniform(1, 3, len(self.dates))
        self.low = self.prices - np.random.uniform(1, 3, len(self.dates))
        self.close = self.prices
        self.volume = pd.Series(
            np.random.randint(1000, 10000, len(self.dates)),
            index=self.dates
        )
    
    def test_ma(self):
        """测试移动平均线计算"""
        ma = TechnicalIndicators.calculate_ma(self.prices, window=5)
        self.assertEqual(len(ma), len(self.prices))
        self.assertTrue(ma.isna().sum() == 4)  # 前4个值为NaN
        self.assertTrue(ma.notna().sum() == len(self.prices) - 4)
    
    def test_ema(self):
        """测试指数移动平均线计算"""
        ema = TechnicalIndicators.calculate_ema(self.prices, window=5)
        self.assertEqual(len(ema), len(self.prices))
        self.assertTrue(ema.notna().all())
    
    def test_rsi(self):
        """测试RSI计算"""
        rsi = TechnicalIndicators.calculate_rsi(self.prices)
        self.assertEqual(len(rsi), len(self.prices))
        # 前window个为NaN，后面为有效区间
        self.assertTrue(rsi.isna().sum() >= 13)
        valid = rsi.dropna()
        self.assertTrue(((valid >= 0) & (valid <= 100)).all())
    
    def test_macd(self):
        """测试MACD计算"""
        macd, signal, hist = TechnicalIndicators.calculate_macd(self.prices)
        self.assertEqual(len(macd), len(self.prices))
        self.assertEqual(len(signal), len(self.prices))
        self.assertEqual(len(hist), len(self.prices))
        # 只判断数值类型
        self.assertTrue(isinstance(macd, pd.Series))
        self.assertTrue(isinstance(signal, pd.Series))
        self.assertTrue(isinstance(hist, pd.Series))
    
    def test_bollinger_bands(self):
        """测试布林带计算"""
        middle, upper, lower = TechnicalIndicators.calculate_bollinger_bands(self.prices)
        self.assertEqual(len(middle), len(self.prices))
        self.assertEqual(len(upper), len(self.prices))
        self.assertEqual(len(lower), len(self.prices))
        # 有效区间内上轨>=中轨>=下轨
        valid = (~middle.isna()) & (~upper.isna()) & (~lower.isna())
        self.assertTrue((upper[valid] >= middle[valid]).all())
        self.assertTrue((lower[valid] <= middle[valid]).all())
    
    def test_atr(self):
        """测试ATR计算"""
        atr = TechnicalIndicators.calculate_atr(self.high, self.low, self.close)
        self.assertEqual(len(atr), len(self.prices))
        # 前window个为NaN
        self.assertTrue(atr.isna().sum() >= 13)
        valid = atr.dropna()
        self.assertTrue((valid >= 0).all())
    
    def test_stochastic(self):
        """测试随机指标计算"""
        k, d = TechnicalIndicators.calculate_stochastic(self.high, self.low, self.close)
        self.assertEqual(len(k), len(self.prices))
        self.assertEqual(len(d), len(self.prices))
        valid_k = k.dropna()
        valid_d = d.dropna()
        self.assertTrue(((valid_k >= 0) & (valid_k <= 100)).all())
        self.assertTrue(((valid_d >= 0) & (valid_d <= 100)).all())
    
    def test_obv(self):
        """测试OBV计算"""
        df = pd.DataFrame({'close': self.close, 'volume': self.volume})
        obv = TechnicalIndicators.calculate_obv(df)
        self.assertEqual(len(obv), len(self.prices))
        self.assertTrue(obv.notna().all())
        # 边界：空df
        empty_df = pd.DataFrame(columns=['close', 'volume'])
        obv_empty = TechnicalIndicators.calculate_obv(empty_df)
        self.assertEqual(len(obv_empty), 0)
        # 边界：缺列
        bad_df = pd.DataFrame({'close': self.close})
        obv_bad = TechnicalIndicators.calculate_obv(bad_df)
        self.assertTrue((obv_bad == 0).all())
        # 边界：有NaN
        df_nan = df.copy()
        df_nan.iloc[5, 0] = np.nan
        obv_nan = TechnicalIndicators.calculate_obv(df_nan)
        self.assertEqual(len(obv_nan), len(df_nan))
        self.assertTrue(obv_nan.notna().all())
    
    def test_ichimoku(self):
        """测试一目均衡图计算"""
        conversion, base, span_a, span_b, lagging = TechnicalIndicators.calculate_ichimoku(
            self.high, self.low
        )
        self.assertEqual(len(conversion), len(self.prices))
        self.assertEqual(len(base), len(self.prices))
        self.assertEqual(len(span_a), len(self.prices))
        self.assertEqual(len(span_b), len(self.prices))
        self.assertEqual(len(lagging), len(self.prices))
        # 有效区间应有数值
        self.assertTrue(span_a.dropna().size > 0)
        self.assertTrue(span_b.dropna().size > 0)
    
    def test_vma(self):
        """测试VMA计算"""
        df = pd.DataFrame({'volume': self.volume})
        vma = TechnicalIndicators.calculate_vma(df, window=5)
        self.assertEqual(len(vma), len(self.volume))
        # 前4个为均值，后面为滑动均值
        self.assertTrue(np.isclose(vma.iloc[4], self.volume.iloc[:5].mean()))
        # 边界：空df
        empty_df = pd.DataFrame(columns=['volume'])
        vma_empty = TechnicalIndicators.calculate_vma(empty_df)
        self.assertEqual(len(vma_empty), 0)
        # 边界：缺列
        bad_df = pd.DataFrame({'close': self.close})
        vma_bad = TechnicalIndicators.calculate_vma(bad_df)
        self.assertTrue(np.isnan(vma_bad).all())
        # 边界：有NaN
        df_nan = df.copy()
        df_nan.iloc[5, 0] = np.nan
        vma_nan = TechnicalIndicators.calculate_vma(df_nan)
        self.assertEqual(len(vma_nan), len(df_nan))
        # volume为NaN时vma应等于窗口内非NaN的均值
        self.assertTrue(np.isclose(vma_nan.iloc[5], df_nan['volume'].iloc[1:6].mean(), equal_nan=True))
    
    def test_vr(self):
        """测试VR计算"""
        df = pd.DataFrame({'volume': self.volume})
        vr = TechnicalIndicators.calculate_vr(df, window=5)
        self.assertEqual(len(vr), len(self.volume))
        # 前window个为NaN
        self.assertTrue(np.isnan(vr.iloc[0]))
        # 边界：空df
        empty_df = pd.DataFrame(columns=['volume'])
        vr_empty = TechnicalIndicators.calculate_vr(empty_df)
        self.assertEqual(len(vr_empty), 0)
        # 边界：缺列
        bad_df = pd.DataFrame({'close': self.close})
        vr_bad = TechnicalIndicators.calculate_vr(bad_df)
        self.assertTrue(np.isnan(vr_bad).all())
        # 边界：有NaN
        df_nan = df.copy()
        df_nan.iloc[5, 0] = np.nan
        vr_nan = TechnicalIndicators.calculate_vr(df_nan)
        self.assertEqual(len(vr_nan), len(df_nan))
        self.assertTrue(np.isnan(vr_nan.iloc[5]))
        # 边界：窗口大于数据长度
        short_df = pd.DataFrame({'volume': self.volume.iloc[:3]})
        vr_short = TechnicalIndicators.calculate_vr(short_df, window=10)
        self.assertEqual(len(vr_short), 3)
        self.assertTrue(np.isnan(vr_short).all())
    
    def test_mfi(self):
        """测试MFI计算"""
        df = pd.DataFrame({
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        })
        mfi = TechnicalIndicators.calculate_mfi(df, window=14)
        self.assertEqual(len(mfi), len(self.close))
        # 前window-1个为NaN
        self.assertTrue(mfi.iloc[:13].isna().all())
        # 边界：空df
        empty_df = pd.DataFrame(columns=['high', 'low', 'close', 'volume'])
        mfi_empty = TechnicalIndicators.calculate_mfi(empty_df)
        self.assertEqual(len(mfi_empty), 0)
        # 边界：缺列
        bad_df = pd.DataFrame({'close': self.close, 'volume': self.volume})
        mfi_bad = TechnicalIndicators.calculate_mfi(bad_df)
        self.assertTrue(np.isnan(mfi_bad).all())
        # 边界：有NaN
        df_nan = df.copy()
        df_nan.iloc[5, 0] = np.nan
        mfi_nan = TechnicalIndicators.calculate_mfi(df_nan)
        self.assertEqual(len(mfi_nan), len(df_nan))
        self.assertTrue(np.isnan(mfi_nan.iloc[5]))
    
    def test_pma(self):
        """测试PMA计算"""
        df = pd.DataFrame({'close': self.close})
        pma = TechnicalIndicators.calculate_pma(df, window=5)
        self.assertEqual(len(pma), len(self.close))
        # 前4个为均值，后面为滑动均值
        self.assertTrue(np.isclose(pma.iloc[4], self.close.iloc[:5].mean()))
        # 边界：空df
        empty_df = pd.DataFrame(columns=['close'])
        pma_empty = TechnicalIndicators.calculate_pma(empty_df)
        self.assertEqual(len(pma_empty), 0)
        # 边界：缺列
        bad_df = pd.DataFrame({'volume': self.volume})
        pma_bad = TechnicalIndicators.calculate_pma(bad_df)
        self.assertTrue(np.isnan(pma_bad).all())
        # 边界：有NaN
        df_nan = df.copy()
        df_nan.iloc[5, 0] = np.nan
        pma_nan = TechnicalIndicators.calculate_pma(df_nan)
        self.assertEqual(len(pma_nan), len(df_nan))
        self.assertTrue(np.isclose(pma_nan.iloc[5], df_nan['close'].iloc[1:6].mean(), equal_nan=True))

if __name__ == '__main__':
    unittest.main() 