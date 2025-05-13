import pandas as pd
import numpy as np
from typing import Tuple
from utils.technical_indicators import TechnicalIndicators

class MACrossStrategy:
    """移动平均线交叉策略"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        """
        初始化策略
        
        Args:
            short_window: 短期移动平均线窗口
            long_window: 长期移动平均线窗口
        """
        self.short_window = short_window
        self.long_window = long_window
        self.indicators = TechnicalIndicators()
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        
        Args:
            data: 价格数据
            
        Returns:
            DataFrame: 包含交易信号的DataFrame
        """
        # 计算移动平均线
        data['short_ma'] = self.indicators.calculate_ma(data['Close'], self.short_window)
        data['long_ma'] = self.indicators.calculate_ma(data['Close'], self.long_window)
        
        # 生成交易信号
        data['signal'] = 0.0
        data.loc[data.index[self.short_window:], 'signal'] = np.where(
            data['short_ma'][self.short_window:] > data['long_ma'][self.short_window:], 1.0, 0.0)
        
        # 生成交易位置
        data['position'] = data['signal'].diff()
        
        return data
    
    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000.0) -> Tuple[float, float, float]:
        """
        回测策略
        
        Args:
            data: 价格数据
            initial_capital: 初始资金
            
        Returns:
            tuple: (总收益率, 年化收益率, 最大回撤)
        """
        # 生成信号
        data = self.generate_signals(data)
        
        # 计算持仓
        data['holdings'] = data['position'] * data['Close']
        
        # 计算现金
        data['cash'] = initial_capital - (data['position'].diff() * data['Close']).cumsum()
        
        # 计算总资产
        data['total'] = data['cash'] + data['holdings']
        
        # 计算收益率
        total_return = (data['total'].iloc[-1] - initial_capital) / initial_capital
        
        # 计算年化收益率
        days = (data.index[-1] - data.index[0]).days
        annual_return = (1 + total_return) ** (365.0 / days) - 1
        
        # 计算最大回撤
        data['peak'] = data['total'].cummax()
        data['drawdown'] = (data['total'] - data['peak']) / data['peak']
        max_drawdown = data['drawdown'].min()
        
        return total_return, annual_return, max_drawdown 