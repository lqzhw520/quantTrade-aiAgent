from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
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
        data = data.copy()
        data['short_ma'] = self.indicators.calculate_ma(data['Close'], self.short_window).fillna(0)
        data['long_ma'] = self.indicators.calculate_ma(data['Close'], self.long_window).fillna(0)
        data['signal'] = 0.0
        data.loc[data.index[self.short_window:], 'signal'] = np.where(
            data['short_ma'][self.short_window:] > data['long_ma'][self.short_window:], 1.0, 0.0)
        data['position'] = data['signal'].diff().fillna(0)
        return data

    def backtest(self, data: pd.DataFrame, initial_capital: float = 100000.0) -> Dict[str, Any]:
        """
        回测策略，返回结构化结果，便于前端 ECharts 可视化
        Args:
            data: 价格数据
            initial_capital: 初始资金
        Returns:
            dict: 包含绩效和图表数据
        """
        try:
            data = self.generate_signals(data)
            data['holdings'] = data['signal'] * data['Close']
            data['cash'] = initial_capital - (data['position'] * data['Close']).cumsum()
            data['total'] = data['cash'] + data['holdings']
            data['peak'] = data['total'].cummax()
            data['drawdown'] = (data['total'] - data['peak']) / data['peak']
            # 绩效指标
            total_return = (data['total'].iloc[-1] - initial_capital) / initial_capital
            days = (data.index[-1] - data.index[0]).days
            annual_return = (1 + total_return) ** (365.0 / days) - 1 if days > 0 else 0
            max_drawdown = data['drawdown'].min()
            # 图表数据
            dates = data.index.strftime('%Y-%m-%d').tolist()
            close_prices = data['Close'].round(2).tolist()
            short_ma = data['short_ma'].round(2).fillna(0).tolist()
            long_ma = data['long_ma'].round(2).fillna(0).tolist()
            # 买卖信号点
            buy_signals = [
                {"date": str(idx.date()), "price": float(row['Close'])}
                for idx, row in data[(data['position'] > 0)].iterrows()
            ]
            sell_signals = [
                {"date": str(idx.date()), "price": float(row['Close'])}
                for idx, row in data[(data['position'] < 0)].iterrows()
            ]
            # 资产曲线
            equity_curve = [
                {"date": str(idx.date()), "value": float(row['total'])}
                for idx, row in data.iterrows()
            ]
            return {
                "performance": {
                    "total_return": round(float(total_return), 4),
                    "annual_return": round(float(annual_return), 4),
                    "max_drawdown": round(float(max_drawdown), 4)
                },
                "chart_data": {
                    "dates": dates,
                    "close_prices": close_prices,
                    "short_ma": short_ma,
                    "long_ma": long_ma,
                    "buy_signals": buy_signals,
                    "sell_signals": sell_signals,
                    "equity_curve": equity_curve
                }
            }
        except Exception as e:
            print(f"回测错误: {str(e)}")
            # 返回一个最小化的结果，避免前端错误
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