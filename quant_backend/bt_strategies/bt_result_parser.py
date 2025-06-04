import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional

class BacktraderResultParser:
    """
    Backtrader回测结果解析器
    
    将backtrader回测结果转换为标准化的JSON格式，与现有API兼容
    """
    
    @staticmethod
    def parse_results(
        cerebro, 
        strategy_instance, 
        data: pd.DataFrame,
        initial_capital: float
    ) -> Dict[str, Any]:
        """
        解析Backtrader回测结果
        
        参数:
            cerebro: Backtrader的Cerebro实例
            strategy_instance: 策略实例
            data: 原始数据DataFrame
            initial_capital: 初始资金
        
        返回:
            Dict: 标准化的回测结果字典
        """
        # 获取最终价值
        final_value = cerebro.broker.getvalue()
        
        # 获取绩效指标
        performance = BacktraderResultParser._calculate_performance(
            cerebro, strategy_instance, initial_capital, final_value, data
        )
        
        # 获取图表数据
        chart_data = BacktraderResultParser._prepare_chart_data(
            strategy_instance, data
        )
        
        # 构建标准化结果
        result = {
            "performance": performance,
            "chart_data": chart_data
        }
        
        return result
    
    @staticmethod
    def _calculate_performance(
        cerebro, 
        strategy_instance, 
        initial_capital: float, 
        final_value: float,
        data: pd.DataFrame
    ) -> Dict[str, float]:
        """计算绩效指标"""
        # 计算总收益率
        total_return = (final_value - initial_capital) / initial_capital
        
        # 获取分析器数据
        analyzers = strategy_instance.analyzers
        
        # 尝试获取夏普比率
        sharpe_ratio = 0.0
        try:
            if hasattr(analyzers, 'sharpe'):
                sharpe_analysis = analyzers.sharpe.get_analysis()
                sharpe_value = sharpe_analysis.get('sharperatio', 0.0)
                # 安全的类型转换和NaN检查
                if sharpe_value is not None:
                    try:
                        sharpe_ratio = float(sharpe_value)
                        if pd.isna(sharpe_ratio) or np.isinf(sharpe_ratio):
                            sharpe_ratio = 0.0
                    except (ValueError, TypeError):
                        sharpe_ratio = 0.0
        except Exception as e:
            print(f"获取夏普比率失败: {str(e)}")
            sharpe_ratio = 0.0
        
        # 尝试获取最大回撤
        max_drawdown = 0.0
        try:
            if hasattr(analyzers, 'drawdown'):
                dd_analysis = analyzers.drawdown.get_analysis()
                dd_value = dd_analysis.get('max', {}).get('drawdown', 0.0)
                # 安全的类型转换
                if dd_value is not None:
                    try:
                        max_drawdown = float(dd_value)
                        # 转换为百分比格式
                        max_drawdown = max_drawdown / 100.0 if max_drawdown > 1.0 else max_drawdown
                        if pd.isna(max_drawdown) or np.isinf(max_drawdown):
                            max_drawdown = 0.0
                    except (ValueError, TypeError):
                        max_drawdown = 0.0
        except Exception as e:
            print(f"获取最大回撤失败: {str(e)}")
            max_drawdown = 0.0
        
        # 尝试获取年化收益率
        annual_return = 0.0
        try:
            if hasattr(analyzers, 'returns'):
                returns_analysis = analyzers.returns.get_analysis()
                if 'rnorm100' in returns_analysis:
                    annual_value = returns_analysis['rnorm100']
                    if annual_value is not None:
                        try:
                            annual_return = float(annual_value) / 100.0  # 标准化为小数
                        except (ValueError, TypeError):
                            annual_return = 0.0
                elif 'ravg' in returns_analysis:
                    annual_value = returns_analysis['ravg']
                    if annual_value is not None:
                        try:
                            annual_return = float(annual_value)
                        except (ValueError, TypeError):
                            annual_return = 0.0
        except Exception as e:
            print(f"获取年化收益率失败: {str(e)}")
            annual_return = 0.0
        
        # 如果通过分析器获取失败，使用简单计算
        if annual_return == 0.0 and isinstance(data.index, pd.DatetimeIndex) and len(data.index) > 0:
            try:
                # 计算交易天数
                time_days = (data.index[-1] - data.index[0]).days
                if time_days > 0:
                    annual_return = (1 + total_return) ** (365.0 / time_days) - 1
            except Exception as e:
                print(f"计算年化收益率失败: {str(e)}")
        
        return {
            "total_return": round(float(total_return), 4),
            "annual_return": round(float(annual_return), 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "sharpe_ratio": round(float(sharpe_ratio), 4)
        }
    
    @staticmethod
    def _prepare_chart_data(strategy_instance, data: pd.DataFrame) -> Dict[str, Any]:
        """准备图表数据"""
        # 获取日期序列
        dates = []
        if isinstance(data.index, pd.DatetimeIndex):
            dates = data.index.strftime('%Y-%m-%d').tolist()
        else:
            # 尝试从trade_time或trade_date列获取日期
            for col in ['trade_time', 'trade_date', 'datetime']:
                if col in data.columns:
                    dates = pd.to_datetime(data[col]).dt.strftime('%Y-%m-%d').tolist()
                    break
            
            # 如果还是没有日期，使用序号替代
            if not dates:
                dates = [str(i) for i in range(len(data))]
        
        # 获取价格序列
        prices = []
        if 'close' in data.columns:
            prices = data['close'].fillna(0).tolist()
        
        # 获取移动平均线数据
        short_ma = []
        long_ma = []
        
        # 尝试从策略实例获取参数
        short_period = getattr(strategy_instance.params, 'short_ma', 20)
        long_period = getattr(strategy_instance.params, 'long_ma', 50)
        
        # 计算移动平均线
        if 'close' in data.columns:
            short_ma = data['close'].rolling(window=short_period).mean().fillna(0).tolist()
            long_ma = data['close'].rolling(window=long_period).mean().fillna(0).tolist()
        
        # 获取交易信号
        signals = strategy_instance.get_signals() if hasattr(strategy_instance, 'get_signals') else {}
        buy_signals = signals.get('buy_signals', [])
        sell_signals = signals.get('sell_signals', [])
        
        # 构建资金曲线
        equity_curve = []
        # 尝试从策略或cerebro获取资金曲线
        try:
            # 创建简单资金曲线
            if len(prices) > 0:
                initial_value = getattr(strategy_instance, 'broker', None)
                if initial_value and hasattr(initial_value, 'startingcash'):
                    initial_value = initial_value.startingcash
                else:
                    initial_value = 100000.0  # 默认值
                
                # 生成简单的资金曲线（仅用于展示，不反映实际交易P&L）
                equity_values = []
                for i, date in enumerate(dates):
                    if i == 0:
                        value = initial_value
                    else:
                        # 简单模拟资金曲线变化
                        price_change = prices[i] / prices[i-1] - 1 if i > 0 and prices[i-1] > 0 else 0
                        value = equity_values[-1] * (1 + price_change * 0.5)  # 只用一半仓位
                    equity_values.append(value)
                
                equity_curve = [
                    {"date": date, "value": value}
                    for date, value in zip(dates, equity_values)
                ]
        except Exception as e:
            print(f"构建资金曲线失败: {str(e)}")
        
        # 将回测结果转换为前端需要的格式
        return {
            "dates": dates,
            "close_prices": prices,
            "short_ma": short_ma,
            "long_ma": long_ma,
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "equity_curve": equity_curve
        }
