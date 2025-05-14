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
        obv = TechnicalIndicators.calculate_obv(self.close, self.volume)
        self.assertEqual(len(obv), len(self.prices))
        self.assertTrue(obv.notna().all())
    
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

if __name__ == '__main__':
    unittest.main() 