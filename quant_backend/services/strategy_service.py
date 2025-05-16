from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from quant_backend.utils.technical_indicators import TechnicalIndicators

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
        """生成交易信号"""
        data = data.copy()
        
        # 统一字段名为小写
        data.columns = data.columns.str.lower()
        
        # 使用技术指标类计算移动平均线
        data['short_ma'] = self.indicators.calculate_pma(data, self.short_window)
        data['long_ma'] = self.indicators.calculate_pma(data, self.long_window)
        
        # 生成交易信号
        data['signal'] = 0.0
        data.loc[data.index[self.long_window:], 'signal'] = np.where(
            data['short_ma'][self.long_window:] > data['long_ma'][self.long_window:], 1.0, 0.0)
        data['position'] = data['signal'].diff()
        
        return data

    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000.0) -> Dict[str, Any]:
        """回测策略"""
        try:
            # 生成交易信号
            data = self.generate_signals(data)
            
            # 计算持仓和现金
            data['holdings'] = data['signal'] * data['close']
            data['cash'] = initial_capital - (data['position'] * data['close']).cumsum()
            data['total'] = data['cash'] + data['holdings']
            
            # 计算回测指标
            data['peak'] = data['total'].cummax()
            data['drawdown'] = (data['total'] - data['peak']) / data['peak']
            
            # 计算收益率指标
            total_return = (data['total'].iloc[-1] - initial_capital) / initial_capital
            days = (data.index[-1] - data.index[0]).days
            annual_return = (1 + total_return) ** (365.0 / days) - 1 if days > 0 else 0
            max_drawdown = data['drawdown'].min()
            
            # 提取买卖信号点
            buy_signals = [
                {"date": str(idx.date()), "price": float(row['close'])}
                for idx, row in data[data['position'] > 0].iterrows()
            ]
            sell_signals = [
                {"date": str(idx.date()), "price": float(row['close'])}
                for idx, row in data[data['position'] < 0].iterrows()
            ]
            
            # 构建返回结果
            return {
                "performance": {
                    "total_return": round(float(total_return), 4),
                    "annual_return": round(float(annual_return), 4),
                    "max_drawdown": round(float(max_drawdown), 4)
                },
                "chart_data": {
                    "dates": data.index.strftime('%Y-%m-%d').tolist(),
                    "close_prices": data['close'].round(2).tolist(),
                    "short_ma": data['short_ma'].round(2).fillna(0).tolist(),
                    "long_ma": data['long_ma'].round(2).fillna(0).tolist(),
                    "buy_signals": buy_signals,
                    "sell_signals": sell_signals,
                    "equity_curve": [
                        {"date": str(idx.date()), "value": float(row['total'])}
                        for idx, row in data.iterrows()
                    ]
                }
            }
        except Exception as e:
            print(f"回测错误: {str(e)}")
            return {
                "performance": {
                    "total_return": 0.0,
                    "annual_return": 0.0,
                    "max_drawdown": 0.0
                },
                "chart_data": {
                    "dates": [],
                    "close_prices": [],
                    "short_ma": [],
                    "long_ma": [],
                    "buy_signals": [],
                    "sell_signals": [],
                    "equity_curve": []
                }
            } 